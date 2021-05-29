import discord
import os
from discord.ext import commands, tasks

# importing database manager
import psycopg2
from psycopg2 import Error

import datetime
from datetime import datetime as dtime

import os
from dotenv import load_dotenv
load_dotenv()
PASS = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
DB_NAME_CODEFORCES = os.getenv("DB_NAME_CF")

conn_forces = psycopg2.connect(f"dbname={DB_NAME_CODEFORCES} host=localhost port={PORT}  user=postgres password={PASS}")

class Codeforces(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # command to gives all the impending or ongoing contest on codeforces
    @commands.command()
    async def codeforces(self, ctx):
        # set up connections
        conn_command = psycopg2.connect(f"dbname={DB_NAME_CODEFORCES} host=localhost port={PORT}  user=postgres password={PASS}")
        c_command = conn_command.cursor()

        # select all contest and store in a list
        c_command.execute("SELECT * FROM Present_Contests ORDER BY START")
        sorted_contests = c_command.fetchall()

        # store today and tomorrows date
        today_date = datetime.date.today()
        tom_delta = datetime.timedelta(hours=24)
        tom_date = today_date + tom_delta

        # if there are no contests
        if len(sorted_contests) == 0:
            await ctx.send("No Codeforces Contests Available :slight_smile:")
            return

        # if contest list is not empty, an embed object is made
        embed = discord.Embed(
            title='__**Upcoming contests**__',
            description='',
            colour=discord.Colour.green()
        )
        embed.set_author(name='Codeforces', icon_url='https://carlacastanho.github.io/Material-de-APC/assets/images/codeforces_icon.png')

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
            e_date = end[:11]

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


    
def setup(client):
    client.add_cog(Codeforces(client))