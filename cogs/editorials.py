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
DB_NAME_EDIT = os.getenv("DB_NAME_EDIT")

class Editorials(commands.Cog):
    def __init__(self, client):
        self.client = client

    # command for getting recent editorials
    @commands.command()
    async def editorials(self, ctx):
        conn_edit = psycopg2.connect(f"dbname={DB_NAME_EDIT} host=localhost port=5432  user=postgres password={PASS}")
        cur_edit = conn_edit.cursor()

        cur_edit.execute("SELECT * FROM editorial_info")
        editorial_list = cur_edit.fetchall()
        print(editorial_list)

        embed = discord.Embed(
            title=f'__**Editorials**__',
            description='',
            colour=discord.Colour.blurple()
        )
        embed.set_author(name='Codechef', icon_url='https://static.dribbble.com/users/70628/screenshots/1743345/codechef.png')

        for i in range(len(editorial_list)):
            embed.add_field(name=str(i+1) + '. ' + '' + '' + editorial_list[i][0] +'' + '', value='[`Find the editorials here`]({})'.format(editorial_list[i][1]), inline=False)

        # embed.set_footer(text='Type "editorials 1" to get URL of the first contest listed here')

        await ctx.send(embed=embed)
        cur_edit.close()
        conn_edit.close()

    
def setup(client):
    client.add_cog(Editorials(client))