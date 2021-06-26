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

TOKEN = os.getenv("TOKEN")
PASS = os.getenv("PASSWORD")
PORT = os.getenv("PORT")
DB_NAME_CHEF = os.getenv("DB_NAME_CC")

conn = psycopg2.connect(f"dbname={DB_NAME_CHEF} host=localhost port={PORT} user=postgres password={PASS}")

class Codechef(commands.Cog):
    def __init__(self, client):
        self.client = client

    # command gives the list of present or future contests on codechef
    @commands.command()
    async def codechef(self, ctx, pre_or_fut='Present', all=None):

        # check if the user has requested present or future contests
        pre_or_fut = pre_or_fut[0].upper() + pre_or_fut[1:].lower()
        if pre_or_fut == "All":
            all = "all"
            pre_or_fut = 'Present'
        elif pre_or_fut not in ['Present', 'Future', "All"]:
            pre_or_fut = 'Present'

        conn_command = psycopg2.connect(f"dbname={DB_NAME_CHEF} host=localhost port={PORT}  user=postgres password={PASS}")
        c_command = conn_command.cursor()

        # store today and tomorrows date
        today_date = datetime.date.today()
        tom_delta = datetime.timedelta(hours=24)
        tom_date = today_date + tom_delta

        # store all contests in a list
        c_command.execute(f"SELECT * FROM {pre_or_fut}_Contests ORDER BY START")
        sorted_contests = c_command.fetchall()

        # function to convert all datetimes to dd mmm yyyy hh:mm:ss' format
        def dtime_conv(date_time):
            date_time = date_time[2][:11] + " " + date_time[2][12:]
            date_time = dtime.strptime(date_time, '%d %b %Y %H:%M:%S')
            return date_time

        # sort contests according to startime
        sorted_contests = sorted(sorted_contests, key=dtime_conv)

        threshold = datetime.timedelta(days=30)
        all_sorted_contests = sorted_contests
        relevant_contests = []

        for contest in sorted_contests:
            time_s = dtime_conv(contest)
            time_e = contest[4]
            if (time_e - time_s) < threshold:
                relevant_contests.append(contest)

        if (all == "all"):
            relevant_contests = sorted_contests

        # in case of no contests available, a message is sent and the function returns
        if len(relevant_contests) == 0:
            await ctx.send("No Contests Available :slight_smile:. Check for longer contests by calling `!codechef all`")
            return

        # if contest list is not empty, an embed object is made
        embed = discord.Embed(
            title=f'__**{pre_or_fut} Contests**__',
            description='',
            colour=discord.Colour.green()
        )
        embed.set_author(name='Codechef', icon_url='https://static.dribbble.com/users/70628/screenshots/1743345/codechef.png')

        # customizing embed format.
        # here, we check if any of the start or end dates are 'today' or 'tomorrow'. If yes, they are
        # replaced by today or tomorrow for better readability
        for i in relevant_contests:
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
            time = '```' + 'Start time' + '  |  ' + 'End time'+'\n' + start + ' |  ' + end +'\n'+ s_time+'    |  '+ e_time +'```'
            embed.add_field(name=name, value=time, inline=False)

        # send embed and close connection
        await ctx.send(embed=embed)
        conn_command.close()


def setup(client):
    client.add_cog(Codechef(client))