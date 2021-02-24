import discord
from discord.ext import commands, tasks

import sqlite3
from sqlite3 import Error

import datetime
from datetime import datetime as dtime
import time

#setting up connections to both the databases
conn = sqlite3.connect('codechef_new.db')
conn_forces = sqlite3.connect('codeforces_new.db')

intents = discord.Intents(messages=True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '!', intents = intents)

#start the task when bot goes online
@client.event
async def on_ready():
    getlist_codechef.start()
    # channel_code=None
    print('hey')

# @client.command
# async def setup(ctx):
#     await ctx.send("put the channel where you want your updates to go")
#     code = await client.wait_for("message", timeout=30)
#     # channel_code = client.get_channel(channel_code)


@client.command()
async def codechef(ctx, pre_or_fut='Present'):
    # await ctx.send(pre_or_fut)
    pre_or_fut = pre_or_fut[0].upper() + pre_or_fut[1:].lower()

    if pre_or_fut not in ['Present', 'Future']:
        pre_or_fut='Present'
    conn_command = sqlite3.connect('codechef_new.db')
    c_command = conn_command.cursor()

    contests = []
    c_command.execute(f"SELECT * FROM `{pre_or_fut} Contests` ORDER BY START")
    sorted_contests = c_command.fetchall()

    # await ctx.send(sorted_contests)
    if len(sorted_contests)==0:
        await ctx.send("No Contests")
        return
    embed = discord.Embed(
        title = f'!{pre_or_fut} Contests On Codechef!',
        description = '',
        colour = discord.Colour.green()
    )
    embed.set_author(name = 'Visit the website <HERE> for more info', url='https://www.codechef.com/')

    if pre_or_fut=='Present':
        for i in sorted_contests:
            name = i[1]
            end_time = i[3][:11] +' '+ i[3][13:]
            embed.add_field(name=name, value=f'Ends on: {end_time}', inline=False)

    else:
        for i in sorted_contests:
            name = i[1]
            start_time = i[2]
            embed.add_field(name=name, value=f'Starts on: {start_time}', inline=False)

    await ctx.send(embed=embed)
    conn_command.close()

@client.command()
async def codeforces(ctx):
    # await ctx.send(pre_or_fut)
    conn_command = sqlite3.connect('codeforces_new.db')
    c_command = conn_command.cursor()

    contests = []
    c_command.execute("SELECT * FROM `Present Contests` ORDER BY START")
    sorted_contests = c_command.fetchall()

    # await ctx.send(sorted_contests)
    if len(sorted_contests)==0:
        await ctx.send("No Contests")
        return
    embed = discord.Embed(
        title = '!Upcoming Contests On Codeforces!',
        description = '',
        colour = discord.Colour.green()
    )
    embed.set_author(name = 'Visit the website <HERE> for more info', url='https://www.codeforces.com/')

    # print(len(sorted_contests))
    # print(sorted_contests)
    for i in sorted_contests:
        name = i[0]
        time = 'Start time: '+ i[1]+ '\nEnds at: ' + i[3]
        embed.add_field(name=name, value=time, inline=False)

    await ctx.send(embed=embed)
    conn_command.close()


@client.event
async def on_reminder(coming, coming_forces):
    channel_code = client.get_channel(808426388716519468)
    if len(coming)==0:
        await channel_code.send("No contests available")
        return
    embed = discord.Embed(
        title = '!Present Contests!',
        description = '',
        colour = discord.Colour.green()
    )
    # embed.set_author(name = 'Visit the website <HERE> for more info', url='https://www.codechef.com/')

    embed.add_field(name='\nCODECHEF',value='Here is the list of ongoing codechef contests', inline=False)
    for i in coming:
        name = i[1]
        start_time = i[2]
        embed.add_field(name=name, value=start_time, inline=False)

    embed.add_field(name='\nCODEFORCES',value='Here is the list of upcoming codeforces contests', inline=False)
    for i in coming_forces:
        name = i[0]
        start_time = i[1]
        embed.add_field(name = name, value= start_time, inline=False)

    if len(coming_forces)==0:
        name = "No Upcoming Contests"
        val = None
        embed.add_field(name = name, value = val, inline=False)

    await channel_code.send(embed=embed)


@tasks.loop(hours=24)
async def getlist_codechef():

    now = dtime.now()
    delta = datetime.timedelta(hours=24)
    bracket = now + delta     # 5 minutes from now

    c = conn.cursor()
    c_forces = conn_forces.cursor()

    c.execute("""SELECT * FROM `Present Contests` ORDER BY START""")
    sorted_events = c.fetchall()    # gets a list of all events sorted by their start time
    c_forces.execute("SELECT * FROM `Present Contests` ORDER BY START")
    sorted_events_forces = c_forces.fetchall()

    upcoming = []     # to store all the events in the next 5 minutes
    upcoming_forces = []

    try:
        most_recent = sorted_events[0]        # chronologically first event, if there are no events it will raise an IndexError
        for event in sorted_events:      #else, store all the events with the same start_time as the upcoming event nto upcoming list
            if dtime.strptime(event[4], '%Y-%m-%d %H:%M:%S')>bracket:
                upcoming.append(event)
            else:
                c.execute("DELETE FROM scheduler WHERE endTime = ?", (event[4],))        # here we have to call another event with this upcoming list as parameter, that will send an embed to a particular channel
    except IndexError:
        print('no contests')
        return


    try:
        for event in sorted_events_forces:
            print(dtime.strptime(event[1], '%Y-%m-%d %H:%M:%S'))
            if dtime.strptime(event[1], '%Y-%m-%d %H:%M:%S')<bracket:
                upcoming_forces.append(event)
            else:
                pass
    except IndexError:
        print('no contests')
        return

    client.dispatch("reminder", upcoming, upcoming_forces)

    print(upcoming, upcoming_forces)

    conn.commit()
    conn_forces.commit()

client.run('ODExNjUxOTg2NDExNzQ5NDQ3.YC1T0Q.hU1YIeMarvDTs6C9bh6qnhNk464')