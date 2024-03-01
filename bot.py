import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Bot

def get_meme():
    response = requests.get('https://meme-api.com/gimme')
    json_data = json.loads(response.text)
    return json_data['url']

bot = Bot(command_prefix = '!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Logged in as {0}!'.format(bot.user))

@bot.command()
async def clear (ctx, limit = 100):
    await ctx.channel.purge(limit=limit)
    embed = discord.Embed(title=f'Deleted {limit} messages in this channel.')
    await ctx.send(embed = embed)

@bot.command()
async def hello(ctx):
    await ctx.send('Vanakam da bunda!')

@bot.command()
async def meme(ctx):
    await ctx.send(get_meme())

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

'''
@bot.command()
async def '''

@bot.command()
async def Help(ctx):
    embed = discord.Embed(title='Help', description='List of available commands:', color=0x00ff00)
    embed.add_field(name='!hello', value='Greets the user', inline=False)
    embed.add_field(name='!meme', value='Sends a random meme', inline=False)
    embed.add_field(name='!ping', value='Returns the latency', inline=False)
    embed.add_field(name='!clear', value='Clears the chat', inline=False)
    await ctx.send(embed=embed)

bot.run('MTIxMzA5NjA0MjMyNTc0NTY2NA.GHgPOy.2QVtV4gXLgrTzLXgudoBJqh5A-9TFubYN1JCO8')
