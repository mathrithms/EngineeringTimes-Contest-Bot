import discord
from discord.ext import commands, tasks

import psycopg2
from psycopg2 import Error

import datetime
from datetime import datetime as dtime

# setting up connections to both the databases
conn = psycopg2.connect("dbname=codechef_new.db host=localhost port=5432 user=postgres password=pass")
conn_forces = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432  user=postgres password=pass")
conn_info = psycopg2.connect("dbname=guild_info.db host=localhost port=5432  user=postgres password=pass")

# switching on intents and defining the bot
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='!', intents=intents)


# start the task when bot goes online
@client.event
async def on_ready():
    getlist.start()
    print('hey')


@client.command()
@commands.has_permissions(manage_messages=True)
async def setup(ctx):
    cursor_info = conn_info.cursor()
    channel = ctx.channel
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


# command gives the list of present or future contests on codechef
@client.command()
async def codechef(ctx, pre_or_fut='Present'):
    # set the default command to present contests
    pre_or_fut = pre_or_fut[0].upper() + pre_or_fut[1:].lower()
    if pre_or_fut not in ['Present', 'Future']:
        pre_or_fut = 'Present'

    conn_command = psycopg2.connect("dbname=codechef_new.db host=localhost port=5432  user=postgres password=pass")
    c_command = conn_command.cursor()

    today_date = datetime.date.today()
    tom_delta = datetime.timedelta(hours=24)
    tom_date = today_date + tom_delta

    # contests = []
    c_command.execute(f"SELECT * FROM {pre_or_fut}_Contests ORDER BY START")
    sorted_contests = c_command.fetchall()

    def dtime_conv(date_time):
        date_time = date_time[2][:11]+" "+date_time[2][12:]
        date_time = dtime.strptime(date_time, '%d %b %Y %H:%M:%S')
        return date_time

    sorted_contests = sorted(sorted_contests, key=dtime_conv)

    # in case of no contests
    if len(sorted_contests) == 0:
        await ctx.send("No Contests Available")
        return

    # if contest list is not empty
    embed = discord.Embed(
        title=f'__**{pre_or_fut} Contests**__',
        description='',
        colour=discord.Colour.green()
    )
    embed.set_author(name='Codechef', icon_url='https://static.dribbble.com/users/70628/screenshots/1743345/codechef.png')

    for i in sorted_contests:
        start = i[2][:11]
        if (dtime.strptime(start, "%d %b %Y").date() == today_date):
            start = 'Today      '
        elif (dtime.strptime(start, "%d %b %Y").date() == tom_date):
            start = 'Tomorrow   '
        s_time = i[2][12:]
        if (s_time[1] == ':'):
            s_time = '0' + s_time

        end = i[3][:11]
        if (dtime.strptime(end, "%d %b %Y").date() == today_date):
            end = 'Today'
        elif (dtime.strptime(end, "%d %b %Y").date() == tom_date):
            end = 'Tomorrow'
        e_time = i[3][12:]
        if (e_time[1] == ':'):
            e_time = '0' + e_time

        name = '__'+'***'+i[1]+'***'+'__'
        time = '```'+'Start time'+'  |  '+'End time'+'\n'+start+' |  '+end+'\n'+s_time+'    |  '+e_time+'```'
        embed.add_field(name=name, value=time, inline=False)

    # send embed and close connection
    await ctx.send(embed=embed)
    conn_command.close()


# this command gives all the impending or ongoing contest on codeforces listed on the website
@client.command()
async def codeforces(ctx):
    # await ctx.send(pre_or_fut)
    conn_command = psycopg2.connect("dbname=codeforces_new.db host=localhost port=5432  user=postgres password=pass")
    c_command = conn_command.cursor()

    # contests = []
    c_command.execute("SELECT * FROM Present_Contests ORDER BY START")
    sorted_contests = c_command.fetchall()

    today_date = datetime.date.today()
    tom_delta = datetime.timedelta(hours=24)
    tom_date = today_date + tom_delta

    # if there are no contests
    if len(sorted_contests) == 0:
        await ctx.send("No Codeforces Contests Available")
        return

    embed = discord.Embed(
        title='__**Upcoming contests**__',
        description='',
        colour=discord.Colour.green()
    )
    embed.set_author(name='Codeforces',
                     icon_url='https://carlacastanho.github.io/Material-de-APC/assets/images/codeforces_icon.png')

    # display starttime and end time of each contest in the embed
    for i in sorted_contests:
        start = i[1]
        s_time = i[1][11:]

        if (s_time[1] == ':'):
            s_time = '0' + s_time

        start = dtime.strptime(start, "%Y-%m-%d %H:%M:%S")
        start = start.strftime("%d %b %Y %H:%M:%S")
        s_date = start[:11]

        if (dtime.strptime(s_date, "%d %b %Y").date() == today_date):
            s_date = 'Today      '
        elif (dtime.strptime(s_date, "%d %b %Y").date() == tom_date):
            s_date = 'Tomorrow   '

        end = i[3]
        e_time = i[3][11:]

        if (e_time[1] == ':'):
            e_time = '0' + e_time

        end = dtime.strptime(end, "%Y-%m-%d %H:%M:%S")
        end = end.strftime("%d %b %Y %H:%M:%S")
        e_date = start[:11]

        if (dtime.strptime(e_date, "%d %b %Y").date() == today_date):
            e_date = 'Today'
        elif (dtime.strptime(e_date, "%d %b %Y").date() == tom_date):
            e_date = 'Tomorrow'

        name = '__'+'***'+i[0]+'***'+'__'
        time = '```'+'Start time'+'  |  '+'Ends at'+'\n'+s_date+' |  '+e_date+'\n'+s_time+'    |  '+e_time+'```'
        embed.add_field(name=name, value=time, inline=False)

    # send embed and close connection
    await ctx.send(embed=embed)
    conn_command.close()


# custom event that is triggered every 24 hrs from the task
@client.event
async def on_reminder1(coming, channel):
    channel_code = client.get_channel(channel)

    today_date = datetime.date.today()
    tom_delta = datetime.timedelta(hours=24)
    tom_date = today_date + tom_delta

    # sorting the contests according to starttime
    def dtime_conv(date_time):
        date_time = date_time[2][:11] + " " + date_time[2][12:]
        date_time = dtime.strptime(date_time, '%d %b %Y %H:%M:%S')
        return date_time

    coming = sorted(coming, key=dtime_conv)

    embed = discord.Embed(
        title='__**Contest Reminder**__',
        description='',
        colour=discord.Colour.green()
    )
    embed.set_author(name='Codechef', icon_url='https://static.dribbble.com/users/70628/screenshots/1743345/codechef.png')

    # setting header
    # n1='__'+'***'+'CODECHEF'+'***'+'__'
    embed.add_field(name=f'{today_date.strftime("%d %B %Y")}',
                    value='__***Ongoing & Upcoming Codechef Contests***__', inline=False)

    # no contests
    if len(coming) == 0:
        name = "__***No Upcoming or Ongoing Codechef Contests***__"
        val = None
        embed.add_field(name=name, value=val, inline=False)

    # if contest list is not empty
    else:
        for i in coming:
            print(i)
            start = i[2][:11]
            if (dtime.strptime(start, "%d %b %Y").date() == datetime.date.today()):
                start = 'Today      '
            elif (dtime.strptime(start, "%d %b %Y").date() == tom_date):
                start = 'Tomorrow   '
            s_time = i[2][12:]
            if (s_time[1] == ':'):
                s_time = '0' + s_time

            end = i[3][:11]
            if (dtime.strptime(end, "%d %b %Y").date() == datetime.date.today()):
                end = 'Today'
            elif (dtime.strptime(end, "%d %b %Y").date() == tom_date):
                end = 'Tomorrow   '
            e_time = i[3][12:]
            if (e_time[1] == ':'):
                e_time = '0' + e_time

            name = '__***'+i[1]+'***__'
            time1 = '```'+'Start time'+'  |  '+'End time'+'\n'+start+' |  '+end+'\n'+s_time+'    |  '+e_time+'```'
            embed.add_field(name=name, value=time1, inline=False)

    await channel_code.send(embed=embed)


@client.event
async def on_reminder2(coming_forces, channel):
    channel_code = client.get_channel(channel)

    today_date = datetime.date.today()
    tom_delta = datetime.timedelta(hours=24)
    tom_date = today_date + tom_delta

    embed = discord.Embed(
        title='__**Contests Reminder**__',
        description='',
        colour=discord.Colour.red()
    )

    embed.set_author(name='Codeforces',
                     icon_url='https://carlacastanho.github.io/Material-de-APC/assets/images/codeforces_icon.png')

    # codeforces
    # n2='__***CODEFORCES***__'
    embed.add_field(name=f'{today_date.strftime("%d %B %Y")}', value='__***Upcoming Codeforces Contests***__', inline=False)
    if len(coming_forces) == 0:
        name = "__***No Upcoming Contests***__"
        val = "No Contest Scheduled Today"
        embed.add_field(name=name, value=val, inline=False)

    # if contest list is not empty
    else:
        for i in coming_forces:
            start = i[1]
            s_time = i[1][11:]
            if (s_time[1] == ':'):
                s_time = '0' + s_time
            start = dtime.strptime(start, "%Y-%m-%d %H:%M:%S")
            start = start.strftime("%d %b %Y %H:%M:%S")
            s_date = start[:11]

            if (dtime.strptime(s_date, "%d %b %Y").date() == datetime.date.today()):
                s_date = 'Today      '
            elif (dtime.strptime(s_date, "%d %b %Y").date() == tom_date):
                s_date = 'Tomorrow   '

            end = i[3]
            e_time = i[3][11:]
            if (e_time[1] == ':'):
                e_time = '0' + e_time
            end = dtime.strptime(end, "%Y-%m-%d %H:%M:%S")
            end = end.strftime("%d %b %Y %H:%M:%S")
            e_date = end[:11]

            if (dtime.strptime(e_date, "%d %b %Y").date() == datetime.date.today()):
                e_date = 'Today'
            elif (dtime.strptime(e_date, "%d %b %Y").date() == tom_date):
                e_date = 'Tomorrow'

            name = '__***'+i[0]+'***__'
            time2 = '```'+'Start time'+'  |  '+'Ends at'+'\n'+s_date+' |  '+e_date+'\n'+s_time+'    |  '+e_time+'```'
            embed.add_field(name=name, value=time2, inline=False)

    await channel_code.send(embed=embed)


# background task that runs every 24 hours
@tasks.loop(hours=24)
async def getlist():

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
    c.execute("""SELECT * FROM Future_Contests ORDER BY START""")
    sorted_events_future = c.fetchall()
    c_forces.execute("SELECT * FROM Present_Contests ORDER BY START")
    sorted_events_forces = c_forces.fetchall()
    print(sorted_events_forces)

    upcoming = []    # stores all ongoing codechef contest
    upcoming_forces = []    # stores all codeforces contests that start in the next 24 hours from now

    # store all ongoing codechef contests in this list
    for event in sorted_events:
        upcoming.append(event)

    for event in sorted_events_future:
        print(dtime.strptime(event[2], '%d %b %Y\n%H:%M:%S'))
        if dtime.strptime(event[2], '%d %b %Y\n%H:%M:%S') < bracket:
            upcoming.append(event)
        else:
            pass

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
                client.dispatch("reminder1", upcoming, int(guild[0]))
                client.dispatch("reminder2", upcoming_forces, int(guild[0]))
            conn_info.commit()
    except Error as e:
        print(e)
        conn_info.rollback()

    print(upcoming, '\n', upcoming_forces)

    conn.commit()
    conn_forces.commit()
client.run('ODExNjUxOTg2NDExNzQ5NDQ3.YC1T0Q._snxU0uQ0AtL1yGlFtojFZ3HfjQ')
