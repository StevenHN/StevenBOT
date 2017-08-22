#! python3
# coding: utf-8

import json
import logging
import random
import sys
import datetime

import discord
from discord.ext import commands

from ext.utils import checks

# logging
logging.basicConfig(level=logging.WARNING)


# JSON load
def load_db():
    with open('db.json') as f:
        return json.load(f)


# Database load
db = load_db()

# bot declaration
prefix = db['prefix']

description = '''Heló, én Steven multifunkciós Discord botja vagyok!.
\nHa esetleg te is használni szeretnél akkor itt elérsz: *link hamarosan*'''
bot = commands.Bot(command_prefix=prefix, description=description, no_pm=True, pm_help=True)

# ads declaration/banning from db
ads = db['ads']
# ads = [".biz"] # tests only
whitelist = db['whitelist']
role_whitelist = db['role_whitelist']
current_datetime = datetime.datetime.now().strftime("%Y %b %d %H:%M")

# Cogs addition
initial_extensions = [
    'ext.admin',
    'ext.mentions',
    'ext.meta',
    'ext.mod',
    # 'ext.profile',
]


# Error handling
@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author,
                               'Ezt a parancsot nem használhatod privátban!')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.channel,
                               'Ez a parancs le van tiltva, vagyis nem használható!')
    elif isinstance(error, commands.CommandInvokeError):
        pass  # do nothing

    elif isinstance(error, commands.CheckFailure):
        await bot.send_message(ctx.message.channel,
                               "Ehhez nincs engedélyed!")
    elif isinstance(error, commands.CommandNotFound):
        await bot.send_message(ctx.message.channel,
                               "Nincs ilyen parancs! _még..._")


@bot.event
async def on_ready():
    print('\nLogged in as')
    print("Felhasználónév: " + bot.user.name)
    print("ID: " + bot.user.id)
    print("Start: " + current_datetime)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    await bot.change_status(game=discord.Game(name=">help | v1.0"), idle=False)


@bot.event
async def on_resumed():
    print('resumed...')


@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
        print("{0} frissítette a nickedet!".format(after))
        for word in ads:
            if word.lower() in str(after.nick).lower():
                try:
                    alert = '{0.mention} nickneve tiltott szavakat tartalmaz!'
                    await bot.send_message(after.server, alert.format(after))
                    await bot.change_nickname(after, '[Nick violates rules]')
                except discord.HTTPException:
                    error = "Hiba történt {0.mention} nickneve változtatása közben!"
                    await bot.send_message(after.server, error.format(after))
            else:
                continue


@bot.event
async def on_server_join(server):
    await bot.send_message(server, "Heló @everyone!")


@bot.command(hidden=True)
@checks.is_owner()
async def user_list():
    """Displays a log of all users in every server the bot is connected to"""
    print("!!!!usrlist!!!! Scannelés")
    await bot.say("A lista a konzolban.")
    print("\nLog datetime: " + current_datetime)
    print("----------------------")
    for server in bot.servers:
        for member in server.members:
            print(
                "szerver: {0} | fh: {1.name} | uid: {1.id} | role: {1.top_role} | role_id: {1.top_role.id}".format(
                    server, member,
                    member))


@bot.command(hidden=True)
async def date_joined(member: discord.Member):
    """Says when a member joined from the bot server's database"""
    await bot.say('{0.name} csatlakozott {0.joined_at}'.format(member))


# run dat shit tho
if __name__ == '__main__':
    if any('debug' in arg.lower() for arg in sys.argv):
        bot.command_prefix = '^'

    bot.client_id = db['client_id']
    bot.carbon_key = db['carbon_key']  # Future carbon integration???? well never know
    bot.bots_key = db['bots_key']

    # load the extensions
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Bővítmény betöltése SIKERTELEN: {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run(db['token'])
