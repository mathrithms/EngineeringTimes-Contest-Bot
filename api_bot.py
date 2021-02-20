import discord
import aiohttp
from discord.ext import commands, tasks
import sqlite3
from sqlite3 import Error


conn = sqlite3.connect('codechef_new.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM `Future Contests`")
items = cursor.fetchall()

intents = discord.Intents(messages=True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '!', intents = intents)

@client.event
async def on_ready():
    print('hey')


@client.command()
async def present(ctx):
    embed = discord.Embed(
        title = '!Present Contests!',
        description = 'Following is the list of present contests on codechef',
        colour = discord.Colour.green()
    )

    embed.set_footer(text = 'To get timings do `!time <contest number>`')
    embed.set_author(name = 'Visit the website for more info', url='https://www.codechef.com/')

    for i in items:
        name = i[1] + ' | ' + i[0]
        start_time = i[2][:11] + f' ({i[2][13:]})'
        embed.add_field(name=name, value=start_time, inline=False)
        # embed.add_field(name='Name', value='Name Value', inline=False)
        # embed.add_field(name='Timing', value='Timing Value', inline=False)

    await ctx.send(embed=embed)


#---------------------------------------------------------------------------------#

#this bot takes FINISHED CONTESTS from API of codeforces and sends name of each to the discord server

@client.command()
async def list_contests(ctx):
    async with aiohttp.ClientSession() as sesh:
        async with sesh.get('https://codeforces.com/api/contest.list?gym=true') as r:
            data = await r.json()
            print('x')
            for i in data["result"]:
                await ctx.send(i["name"])
    
    # url = 'https://codeforces.com/api/contest.list?gym=true'
    # async with request("GET", url, headers={}) as response:
    #     data = response.json()
    #     print(type(data["name"]))


client.run('TOKEN')