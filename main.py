import discord
import os
from discord.ext import commands, tasks
  
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")
PASS = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
DB_NAME_CHEF = os.getenv("DB_NAME_CC")
DB_NAME_CODEFORCES = os.getenv("DB_NAME_CF")
DB_NAME_GUILDS = os.getenv("DB_NAME_GUILDS")

# importing database manager
import psycopg2
from psycopg2 import Error

import datetime
from datetime import datetime as dtime

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# setting up connections to both the databases
conn = psycopg2.connect(f"dbname={DB_NAME_CHEF} host=localhost port={PORT} user=postgres password={PASS}")
conn_forces = psycopg2.connect(f"dbname={DB_NAME_CODEFORCES} host=localhost port={PORT}  user=postgres password={PASS}")
conn_info = psycopg2.connect(f"dbname={DB_NAME_GUILDS} host=localhost port={PORT} user=postgres password={PASS}")

# load all the commands when bot goes online
@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# start the tasks when bot goes online
@client.event
async def on_ready():
    getlist.start()
    print('hey')


# custom event that is triggered every 24 hrs and sends all the codechef contest
@client.event
async def on_reminder_chef(coming,channel):

    # get the channel ID from the string passed
    channel_code = client.get_channel(channel)

    # get today and tomorrows dates
    today_date = datetime.date.today()
    tom_delta = datetime.timedelta(hours=24)
    tom_date = today_date + tom_delta

    # function to convert datetimes to dd mmm yyyy hh:mm:ss' format
    def dtime_conv(date_time):
        date_time = date_time[2][:11] + " "+ date_time[2][12:]
        date_time = dtime.strptime(date_time, '%d %b %Y %H:%M:%S')
        return date_time

    # sort all the codechef contests sorted by startime
    coming = sorted(coming, key=dtime_conv)

    # make an Embed object
    embed = discord.Embed(
        title='__**Contest Reminder**__',
        description='',
        colour=discord.Colour.green()
    )
    embed.set_author(name='Codechef', icon_url='https://static.dribbble.com/users/70628/screenshots/1743345/codechef.png')

    # setting header
    n1='__'+'***'+'CODECHEF'+'***'+'__'   #REMOVE THIS LINE
    embed.add_field(name=f'{today_date.strftime("%d %B %Y")}', value='__***Ongoing & Upcoming Codechef Contests***__', inline=False)

    # in case of no contests
    if len(coming) == 0:
        name = "__***No Upcoming or Ongoing Codechef Contests***__"
        val = None
        embed.add_field(name=name, value=val, inline=False)

    # if contest list is not empty
    else:
        for i in coming:
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
            time1= '```'+'Start time'+'  |  '+'End time'+'\n'+start +' |  '+ end +'\n'+ s_time +'    |  '+ e_time +'```'
            embed.add_field(name=name, value=time1, inline=False)

   
    await channel_code.send(embed=embed)

# custom event that gets triggered every 24 hrs and sends codechef contests
@client.event
async def on_reminder_forces(coming_forces, channel):

    # get the channel ID from the string passed
    channel_code = client.get_channel(channel)

    # get today and tomorrows dates
    today_date = datetime.date.today()
    tom_delta = datetime.timedelta(hours=24)
    tom_date = today_date + tom_delta

    # make an Embed object
    embed = discord.Embed(
        title='__**Contests Reminder**__',
        description='',
        colour=discord.Colour.red()
    )

    embed.set_author(name='Codeforces', icon_url='https://carlacastanho.github.io/Material-de-APC/assets/images/codeforces_icon.png')

    # setting header
    n2='__***CODEFORCES***__'
    embed.add_field(name=f'{today_date.strftime("%d %B %Y")}', value='__***Upcoming Codeforces Contests***__', inline=False)

    # in case of no contests
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
            time2 = '```'+'Start time'+'  |  '+'Ends at'+'\n'+ s_date +' |  '+ e_date +'\n'+ s_time +'    |  '+ e_time +'```'
            embed.add_field(name=name, value=time2, inline=False)

    await channel_code.send(embed=embed)


# background task that runs every 24 hours and triggers the custom events
@tasks.loop(hours=24)
async def getlist():

    # creating a time delta of 24 hrs
    now = dtime.now()
    delta = datetime.timedelta(hours=24)
    bracket = now + delta

    # setting up connections
    c = conn.cursor()
    c_forces = conn_forces.cursor()

    # getting server list of the bot
    server_list = client.guilds
    cursor_info = conn_info.cursor()

    # takes each contest in Present Contests table of codechef and each contest in the codeforces table
    # sort them according to start time and put them in lists
    c.execute("""SELECT * FROM Present_Contests ORDER BY START""")
    sorted_events_present = c.fetchall()
    c.execute("""SELECT * FROM Future_Contests ORDER BY START""")
    sorted_events_future = c.fetchall()
    c_forces.execute("SELECT * FROM Present_Contests ORDER BY START")
    sorted_events_forces = c_forces.fetchall()
    print(sorted_events_forces)

    upcoming_chef = []    # stores all ongoing codechef contest
    upcoming_forces = []    # stores all codeforces contests that start in the next 24 hours from now

    # store all ongoing codechef contests in this list
    for event in sorted_events_present:
        upcoming_chef.append(event)

    # checking if any future codechef events start within 24 hrs
    for event in sorted_events_future:
        print(dtime.strptime(event[2], '%d %b %Y\n%H:%M:%S'))   # REMOVE THIS LINE
        if dtime.strptime(event[2], '%d %b %Y\n%H:%M:%S') < bracket:
            upcoming_chef.append(event)
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
        for i in server_list:
            # check which channel has been mapped to which server ID
            guild_id = str(i.id)
            cursor_info.execute("SELECT CHANNEL FROM info WHERE GUILD =%s", (guild_id,))
            guild = cursor_info.fetchone()

            # if a channel is not found, it means it has not been set up
            if guild is None:
                print(f'channel has not been set on "{i.name}"')

            # if found, send embed
            elif guild is not None:
                client.dispatch("reminder_chef", upcoming_chef,int(guild[0]))
                client.dispatch("reminder_forces", upcoming_forces,int(guild[0]))
            conn_info.commit()
    except Error as e:
        print(e)
        conn_info.rollback()

    print(upcoming_chef, '\n', upcoming_forces)

    conn.commit()
    conn_forces.commit()


client.run(TOKEN)