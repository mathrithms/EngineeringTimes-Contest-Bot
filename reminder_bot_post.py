import discord
from discord.ext import commands, tasks

import psycopg2
from psycopg2 import Error

import datetime
from datetime import datetime as dtime
import time

#setting up connections to both the databases
conn = psycopg2.connect("dbname=codechef_new.db host=localhost port=5432 user=postgres password= pass")
conn_forces = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432 user=postgres password=pass")


#switching on intents and defining the bot
intents = discord.Intents(messages=True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '!', intents = intents)

#start the task when bot goes online
@client.event
async def on_ready():
    getlist_codechef.start()            #start the task when bot goes online
    print('hey')

# @client.command
# async def setup(ctx):
#     await ctx.send("put the channel where you want your updates to go")
#     code = await client.wait_for("message", timeout=30)
#     # channel_code = client.get_channel(channel_code)


#command gives the list of present or future contests on codechef
@client.command()
async def codechef(ctx, pre_or_fut='Present'):
    #set the default command to present contests
    pre_or_fut = pre_or_fut[0].upper() + pre_or_fut[1:].lower()
    if pre_or_fut not in ['Present', 'Future']:
        pre_or_fut='Present'
    
    conn_command =  psycopg2.connect("dbname=codechef_new.db host=localhost port=5432 user=postgres password= pass")
    c_command = conn_command.cursor()

    contests = []
    c_command.execute(f"SELECT * FROM Present_Contests ORDER BY START")
    sorted_contests = c_command.fetchall()

    #in case of no contests
    if len(sorted_contests)==0:
        await ctx.send("No Contests")
        return

    #if contest list is not empty   
    embed = discord.Embed(
        title = f'!{pre_or_fut} Contests On Codechef!',
        description = '',
        colour = discord.Colour.green()
    )
    embed.set_author(name = 'Visit the website <HERE> for more info', url='https://www.codechef.com/')

    #if present contests are requested
    if pre_or_fut=='Present':
        for i in sorted_contests:
            name = i[1]
            end_time = i[3][:11] +' '+ i[3][13:]
            embed.add_field(name=name, value=f'Ends on: {end_time}', inline=False)

    #if future contests are requested
    else:
        for i in sorted_contests:
            name = i[1]
            start_time = i[2]
            embed.add_field(name=name, value=f'Starts on: {start_time}', inline=False)

    #send embed and close connection
    await ctx.send(embed=embed)
    conn_command.close()


#this command gives all the impending or ongoing contest on codeforces listed on the website
@client.command()
async def codeforces(ctx):
    conn_command = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432 user=postgres password=pass")
    c_command = conn_command.cursor()

    contests = []
    c_command.execute("SELECT * FROM Present_Contests ORDER BY START")
    sorted_contests = c_command.fetchall()

    #if there are no contests
    if len(sorted_contests)==0:
        await ctx.send("No Contests")
        return
    embed = discord.Embed(
        title = '!Upcoming Contests On Codeforces!',
        description = '',
        colour = discord.Colour.green()
    )
    embed.set_author(name = 'Visit the website <HERE> for more info', url='https://www.codeforces.com/')

    #display starttime and end time of each contest in the embed
    for i in sorted_contests:
        name = i[0]
        time = 'Start time: '+ i[1]+ '\nEnds at: ' + i[3]
        embed.add_field(name=name, value=time, inline=False)

    #send embed and close connection
    await ctx.send(embed=embed)
    conn_command.close()


#custom event that is triggered every 24 hrs from the task
@client.event
async def on_reminder(coming, coming_forces):
    #set the channel
    channel_code = client.get_channel(808426388716519468)

    #in case of no ongoing codechef contests i.e. Present Contest table is empty
    if len(coming)==0:
        await channel_code.send("No contests available")
        return
    embed = discord.Embed(
        title = '!Present Contests!',
        description = '',
        colour = discord.Colour.green()
    )

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


#background task that runs every 24 hours
@tasks.loop(hours=24)
async def getlist_codechef():

    #creating 2 datetime objects, current time and 24 hrs later
    now = dtime.now()
    delta = datetime.timedelta(hours=24)
    bracket = now + delta   

    #setting up connections
    c = conn.cursor()
    c_forces = conn_forces.cursor()

    #take each contest in Present Contests table of codechef and each contest in the codeforces table
    #sort them according to start time and put them in lists
    c.execute("""SELECT * FROM Present_Contests ORDER BY START""")
    sorted_events = c.fetchall()    
    c_forces.execute("SELECT * FROM Present_Contests ORDER BY START")
    sorted_events_forces = c_forces.fetchall()

    upcoming = []     #stores all ongoing codechef contest
    upcoming_forces = []        #stores all codeforces contests that start in the next 24 hours from now

    #store all ongoing codechef contests in this list
    for event in sorted_events:      
        upcoming.append(event)

    #check which codeforces contest start in next 24 hours
    for event in sorted_events_forces:
        print(dtime.strptime(event[1], '%Y-%m-%d %H:%M:%S'))
        if dtime.strptime(event[1], '%Y-%m-%d %H:%M:%S')<bracket:
            upcoming_forces.append(event)
        else:
            pass
    
    # passing the upcoming contests to the reminder event.
    client.dispatch("reminder", upcoming, upcoming_forces)
    print(upcoming, upcoming_forces)
    conn.commit()
    conn_forces.commit()

client.run('ODExNjUxOTg2NDExNzQ5NDQ3.YC1T0Q.L0xrbM144xAwypiIi5T5w0xEFc0')