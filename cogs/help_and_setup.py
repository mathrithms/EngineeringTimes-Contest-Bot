from cogs.code_chef import PORT
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

conn_info = psycopg2.connect(f"dbname=guild_info.db host=localhost port={PORT} user=postgres password={PASS}")

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def setup(self, ctx):
        cursor_info = conn_info.cursor()
        channel = ctx.channel
        
        # getting server ID as string to navigate the database
        server = str(ctx.guild.id)
        cursor_info.execute("SELECT CHANNEL FROM info WHERE GUILD = %s", (server, ))

        # storing the row which contains this server ID
        old_channel = cursor_info.fetchone()

        # in case of no such row in database, new row will be made
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

    # help command
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title=f'**Commands**',
            description='',
            colour=discord.Colour.dark_blue()
        )

        name_set = "**__setup__**: *Command to setup the new bot*"
        val_set =  "*No Subcommands*"
        embed.add_field(name=name_set, value=val_set, inline=False)

        name_cc = "**__codechef__**: *Command to give codechef data*"
        val_cc = "__Subcommands__: *present/future*, *lt/lc/cf*"
        embed.add_field(name=name_cc, value=val_cc, inline=False)

        name_cf = "**__codeforces__**: *Command to give codeforces data*"
        val_cf = "*No Subcommands*"
        embed.add_field(name=name_cf, value=val_cf, inline=False)

        name_ed = "**editorials**: *Command to give codechef editorials*"
        val_cf = "*No Subcommands*"
        embed.add_field(name=name_cf, value=val_cf, inline=False)

        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Help(client))