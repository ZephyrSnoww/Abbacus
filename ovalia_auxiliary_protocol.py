from datetime import datetime, timedelta
from time import localtime, strftime
from termcolor import colored
import discord
import json
import os


def clear(): return os.system("cls")


def getJson(_file):
    try:
        with open(f"{_file}.json", "r") as file:
            return json.loads(file.read())
    except IOError:
        return {}


def setJson(_file, _data):
    with open(f"{_file}.json", "w+") as file:
        file.write(json.dumps(_data, indent=4))


async def tryDelete(_ctx):
    try:
        await _ctx.message.delete()
    except:
        pass


def makeEmbed(title="TITLE", description="DESCRIPTION", color=0xffadb6, ctx=None):
    if ctx:
        user_color = getJson(f"users/{ctx.author.id}").get("color")
        _out = discord.Embed(title=title, description=description, color=user_color if user_color else color, timestamp=datetime.now()+timedelta(hours=7))
    else:
        _out = discord.Embed(title=title, description=description, color=color, timestamp=datetime.now())
    if ctx:
        _out.set_author(name=ctx.author.nick if ctx.author.nick else ctx.author.name, icon_url=ctx.author.avatar_url)
    return _out


def hexToRGB(hexIn):
    return tuple(int(hexIn[i:i + 2], 16) for i in (0, 2, 4))


def getTime():
    return strftime("%m/%d/%Y %I:%M:%S %p", localtime())


def log(text="PLACEHOLDER", cog="Main", color="green", ctx=None, event=False):
    if ctx:
        if event:
            print("[%s] [%s] [%s] %s [%s] %s %s" % (getTime(), colored("Abacus", "blue"), colored(cog, color), ("." * (20 - len(cog))), ("Direct Message" if not ctx.guild else ctx.guild.name), ("." * (20 - len("Direct Message" if not ctx.guild else ctx.guild.name))), text))
        else:
            print("[%s] [%s] [%s] %s [%s] %s [%s] %s %s" % (getTime(), colored("Abacus", "blue"), colored(cog, color), ("." * (20 - len(cog))), ("Direct Message" if not ctx.guild else ctx.guild.name), ("." * (20 - len("Direct Message" if not ctx.guild else ctx.guild.name))), ctx.author.name, ("." * (20 - len(ctx.author.name))), text))
    else:
        print("[%s] [%s] [%s] %s %s" % (getTime(), colored("Abacus", "blue"), colored(cog, color), ("." * (20 - len(cog))), text))


# Valid Termcolor Colors:
#  - grey
#  - white

#  - green
#  - yellow
#  - blue
#  - cyan
#  - magenta
#  - red