from asyncio.tasks import wait_for
import discord
import os
from discord.ext import commands, tasks
from discord.message import Message
import asyncio
from main import client

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

        cur_edit.execute("SELECT * FROM editorial_info")    # getting list of editorials
        editorial_list = cur_edit.fetchall()

        embed_list = []      # list to store embeds with 5 field each. this is done to ensure the chat is not flooded by long embeds 

        num_of_pages = len(editorial_list) if (len(editorial_list)%5==0) else len(editorial_list)//5 + 1      # number of embed pages

        for i in range(len(editorial_list)//5 + 1):
            embed = discord.Embed(
                title=f'__**Editorials**__',
                description='',
                colour=discord.Colour.blurple(),
            )
            embed.set_author(name='Codechef', icon_url='https://static.dribbble.com/users/70628/screenshots/1743345/codechef.png')
            embed.set_footer(text=f"Page {i+1}/{num_of_pages}")
            embed_list.append(embed)

        current_embed_num = 0
        current_embed = embed_list[current_embed_num]
        

        # loop to divide embed fields into groups of five
        for i in range(len(editorial_list)):
            if (i%5==0 and i!=0):
                current_embed_num += 1
                current_embed = embed_list[current_embed_num]
            current_embed.add_field(name=str(i+1) + '. ' + '' + '' + editorial_list[i][0] + '' + '', value='[`Find the editorials here`]({})'.format(editorial_list[i][1]), inline=False)


        msg = await ctx.send(embed=embed_list[0])

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == '➡️' or str(reaction.emoji) == '⬅️')

        await msg.add_reaction('⬅️')    # emoji reactions to navigate between pages
        await msg.add_reaction('➡️')

        cur_edit.close()
        conn_edit.close()

        i=0
        max = len(embed_list) - 1
        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout = 10.0, check = check)
                await msg.remove_reaction(reaction, user)
            except:
                break

            if str(reaction) == '⬅️':
                if i > 0:
                    i -= 1
                    await msg.edit(embed = embed_list[i])

            elif str(reaction) == '➡️':
                if i < max:
                    i += 1 
                    await msg.edit(embed = embed_list[i])

    
def setup(client):
    client.add_cog(Editorials(client))