import os

from discord.ext import commands
from dotenv import load_dotenv
from fidelityAPI import fidelity
import discord

load_dotenv()
user = os.getenv('FID_USERNAME')
pswd = os.getenv('FID_PASSWORD')
token = os.getenv('TOKEN')

f = fidelity(user, pswd)
intents = discord.Intents.default()
intents.message_content = True
intents.typing = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    for server in bot.guilds:
        for channel in server.channels:
            if str(channel.type) == 'text':
                await channel.send('Started')


@bot.command(name='buy')
async def buy(ctx, stocks, accounts=None):
    await ctx.send('Working...')
    async with ctx.typing():
        if accounts is None:
            await f.bs(ctx, True, stocks.split(','))
        else:
            await f.bs(ctx, True, stocks.split(','), accounts.split(','))


@bot.command(name='sell')
async def sell(ctx, stocks, accounts=None):
    await ctx.send('Working...')
    async with ctx.typing():
        if accounts is None:
            await f.bs(ctx, False, stocks.split(','))
        else:
            await f.bs(ctx, False, stocks.split(','), accounts.split(','))

@bot.command(name='balances')
async def balances(ctx, accounts=None):
    await ctx.send('Working...')
    async with ctx.typing():
        response = await f.check_balances(ctx)
        total = 0
        if accounts is None:
            for account, balance in response.items():
                await ctx.send(f'{account}: {balance}')
                total += float(balance[1:])
            await ctx.send(f'Total: ${round(total, 2)}')
        else:
            accounts = accounts.split(',')
            for account in accounts:
                for account1, balance in response.items():
                    if account1 == account:
                        await ctx.send(f'{account}: {balance}')
                        total += float(balance[1:])
            await ctx.send(f'Total: ${round(total, 2)}')

bot.run(token)
