import discord
from discord.ext import commands, tasks

import psycopg2

import datetime
from datetime import datetime as dtime

# setting up connections to both the databases
conn = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432 user=postgres password=Samarth@1729")
conn_forces = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432 user=postgres password=Samarth@1729")
conn_info = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432 user=postgres password=Samarth@1729")

# switching on intents and defining the bot
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='!', intents=intents)


# start the task when bot goes online
@client.event
async def on_ready():
    getlist_codechef.start()
    print('hey')


@client.command()
async def setup(ctx, channel: discord.TextChannel):
    cursor_info = conn_info.cursor()

    # getting server ID as string to navigate the database
    server = str(ctx.guild.id)
    cursor_info.execute("SELECT CHANNEL FROM info WHERE GUILD = %s", (server, ))

    # storing the row which contains this server ID
    old_channel = cursor_info.fetchone()

    # in case of no such row, new row will be made
    if old_channel is None:
        cursor_info.execute(("INSERT INTO info VALUES (%s, %s, %s)"), (server, str(channel.id), ctx.guild.name))
        await ctx.send(f"Your channel has been set to {channel.mention}")

    # if row is already there, channel ID will be updated
    elif old_channel is not None:
        cursor_info.execute(("UPDATE info SET CHANNEL = %s WHERE GUILD = %s"), (str(channel.id), server))
        await ctx.send(f"Your channel has been updated to {channel.mention}")

    # save changes and close connection
    conn_info.commit()
    cursor_info.close()


# handling errors in setup command
@setup.error
async def setup_error(ctx, error):
    # if no channel is given
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Pass a channel ID')

    # if invalid channel is given
    elif isinstance(error, commands.ChannelNotFound):
        await ctx.send('Pass a valid channel ID, this is invalid')


# command gives the list of present or future contests on codechef
@client.command()
async def codechef(ctx, pre_or_fut='Present'):
    # set the default command to present contests
    pre_or_fut = pre_or_fut[0].upper() + pre_or_fut[1:].lower()
    if pre_or_fut not in ['Present', 'Future']:
        pre_or_fut = 'Present'

    conn_command = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432 user=postgres password=Samarth@1729")
    c_command = conn_command.cursor()

    # contests = []
    c_command.execute(f"SELECT * FROM {pre_or_fut}_Contests ORDER BY START")
    sorted_contests = c_command.fetchall()

    # in case of no contests
    if len(sorted_contests) == 0:
        await ctx.send("No Contests")
        return

    # if contest list is not empty
    embed = discord.Embed(
        title=f'!{pre_or_fut} Contests On Codechef!',
        description='',
        colour=discord.Colour.green()
    )
    embed.set_author(name='Visit the website <HERE> for more info', url='https://www.codechef.com/')

    # if present contests are requested
    if pre_or_fut == 'Present':
        for i in sorted_contests:
            name = i[1]
            end_time = i[3][:11] + ' ' + i[3][13:]
            embed.add_field(name=name, value=f'Ends on: {end_time}', inline=False)

    # if future contests are requested
    else:
        for i in sorted_contests:
            name = i[1]
            start_time = i[2]
            embed.add_field(name=name, value=f'Starts on: {start_time}', inline=False)

    # send embed and close connection
    await ctx.send(embed=embed)
    conn_command.close()


# this command gives all the impending or ongoing contest on codeforces listed on the website
@client.command()
async def codeforces(ctx):
    # await ctx.send(pre_or_fut)
    conn_command = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432 user=postgres password=Samarth@1729")
    c_command = conn_command.cursor()

    # contests = []
    c_command.execute("SELECT * FROM Present_Contests ORDER BY START")
    sorted_contests = c_command.fetchall()

    # if there are no contests
    if len(sorted_contests) == 0:
        await ctx.send("No Contests")
        return

    embed = discord.Embed(
        title='!Upcoming Contests On Codeforces!',
        description='',
        colour=discord.Colour.green()
    )
    embed.set_author(name='Visit the website <HERE> for more info', url='https://www.codeforces.com/')

    # display starttime and end time of each contest in the embed
    for i in sorted_contests:
        name = i[0]
        time = 'Start time: ' + i[1] + '\nEnds at: ' + i[3]
        embed.add_field(name=name, value=time, inline=False)

    # send embed and close connection
    await ctx.send(embed=embed)
    conn_command.close()


# custom event that is triggered every 24 hrs from the task
@client.event
async def on_reminder(coming, coming_forces, channel):
    channel_code = client.get_channel(channel)

    # in case of no ongoing codechef contests i.e. Present Contest table is empty

    embed = discord.Embed(
        title='!Present Contests!',
        description='',
        colour=discord.Colour.green()
    )

    # codechef
    embed.add_field(name='\nCODECHEF', value='Here is the list of ongoing codechef contests', inline=False)

    # no contests
    if len(coming) == 0:
        name = "No Upcoming Contests"
        val = None
        embed.add_field(name=name, value=val, inline=False)

    # if contest list is not empty
    else:
        for i in coming:
            name = i[1]
            start_time = i[2]
            embed.add_field(name=name, value=start_time, inline=False)

    # codeforces
    embed.add_field(name='\nCODEFORCES', value='Here is the list of upcoming codeforces contests', inline=False)
    if len(coming_forces) == 0:
        name = "No Upcoming Contests"
        val = None
        embed.add_field(name=name, value=val, inline=False)

    # if contest list is not empty
    for i in coming_forces:
        name = i[0]
        start_time = i[1]
        embed.add_field(name=name, value=start_time, inline=False)

    await channel_code.send(embed=embed)


# background task that runs every 24 hours
@tasks.loop(hours=24)
async def getlist_codechef():

    # creating 2 datetime objects, current time and 24 hrs later
    now = dtime.now()
    delta = datetime.timedelta(hours=24)
    bracket = now + delta

    # setting up connections
    c = conn.cursor()
    c_forces = conn_forces.cursor()

    # server list of client
    a = client.guilds
    cursor_info = conn_info.cursor()

    # take each contest in Present Contests table of codechef and each contest in the codeforces table
    # sort them according to start time and put them in lists
    c.execute("""SELECT * FROM Present_Contests ORDER BY START""")
    sorted_events = c.fetchall()
    c_forces.execute("SELECT * FROM Present_Contests ORDER BY START")
    sorted_events_forces = c_forces.fetchall()
    print(sorted_events_forces)

    upcoming = []    # stores all ongoing codechef contest
    upcoming_forces = []    # stores all codeforces contests that start in the next 24 hours from now

    # store all ongoing codechef contests in this list
    for event in sorted_events:
        upcoming.append(event)

    # check which codeforces contest start in next 24 hours
    for event in sorted_events_forces:
        print(dtime.strptime(event[1], '%Y-%m-%d %H:%M:%S'))
        if dtime.strptime(event[1], '%Y-%m-%d %H:%M:%S') < bracket:
            upcoming_forces.append(event)
        else:
            pass

    try:
        for i in a:
            # check which channel has been mapped to which server
            guild_id = str(i.id)
            cursor_info.execute("SELECT CHANNEL FROM info WHERE GUILD =%s", (guild_id,))
            guild = cursor_info.fetchone()

            # if a channel is not found, it means it has not been set up
            if guild is None:
                print(f'channel has not been set on "{i.name}"')

            # if found, send embed
            elif guild is not None:
                client.dispatch("reminder", upcoming, upcoming_forces, int(guild[0]))
            conn_info.commit()
    except:
        conn_info.rollback()

    print(upcoming, '\n', upcoming_forces)

    conn.commit()
    conn_forces.commit()

client.run('INSERT TOKEN')
