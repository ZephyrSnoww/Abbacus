from datetime import datetime, timedelta
from time import localtime, strftime
from termcolor import colored
import discord
import json
import os


def clear(): return os.system("cls")

linebreak = "\n"
skills = {
    "acr": "Acrobatics",
    "ani": "Animal Handling",
    "arc": "Arcana",
    "ath": "Athletics",
    "dec": "Deception",
    "his": "History",
    "ins": "Insight",
    "itm": "Intimidation",
    "inv": "Investigation",
    "med": "Medicine",
    "nat": "Nature",
    "prc": "Perception",
    "prf": "Performance",
    "per": "Persuasion",
    "rel": "Religion",
    "slt": "Sleight of Hand",
    "ste": "Stealth",
    "sur": "Survival"
}
mods = {
    1: -5,
    2: -4,
    3: -4,
    4: -3,
    5: -3,
    6: -2,
    7: -2,
    8: -1,
    9: -1,
    10: 0,
    11: 0,
    12: 1,
    13: 1,
    14: 2,
    15: 2,
    16: 3,
    17: 3,
    18: 4,
    19: 4,
    20: 5,
    21: 5,
    22: 6,
    23: 6,
    24: 7,
    25: 7,
    26: 8,
    27: 8,
    28: 9,
    29: 9,
    30: 10
}
abilities = {
    "str": "Strength",
    "dex": "Dexterity",
    "con": "Constitution",
    "int": "Intelligence",
    "wis": "Wisdom",
    "cha": "Charisma"
}
colors = {
    None: "green",
    "Main": "green",
    "DND": "magenta",
    "Events": "magenta",
    "General": "cyan",
    "Images": "red",
    "Settings": "yellow",
    "Moderation": "red"
}


# class 


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


def makeEmbed(
    title="TITLE",
    description="DESCRIPTION",
    color=0xffadb6,
    ctx=None,
    timestamp=datetime.now()+timedelta(hours=6),
    author=None):

    if not color:
        color = 0xffadb6

    if ctx:
        user_color = getJson(f"users/{ctx.author.id}").get("color")
        if timestamp:
            _out = discord.Embed(title=title, description=description, color=user_color if user_color else color, timestamp=timestamp)
        else:
            _out = discord.Embed(title=title, description=description, color=user_color if user_color else color)
    else:
        if timestamp:
            _out = discord.Embed(title=title, description=description, color=color, timestamp=timestamp)
        else:
            _out = discord.Embed(title=title, description=description, color=color)
    if author:
        _out.set_author(name=author.nick if author.nick else author.name, icon_url=author.avatar_url)
    elif ctx:
        _out.set_author(name=ctx.author.nick if ctx.author.nick else ctx.author.name, icon_url=ctx.author.avatar_url)
    return _out


async def give_error(
    text=None,
    categories=None,
    category_title="Categories",
    examples=None,
    ctx=None):

    if not text:
        raise ValueError("Text for the embed description must be given")

    if not ctx:
        raise ValueError("Context must be given")
    
    embed = makeEmbed(
        title="Whoops!",
        description=f"{text}",
        ctx=ctx)

    if categories:
        embed.add_field(
            name=f"Valid {category_title}",
            value=f"{linebreak.join(categories)}",
            inline=False)

    if examples:
        embed.add_field(
            name="Examples",
            value=f"{linebreak.join(examples)}",
            inline=False)

    return await ctx.send(embed=embed)

async def give_output(
    embed_title=None,
    embed_description=None,
    embed=None,
    log_text=None,
    cog=None,
    ctx=None,
    data=None,
    data_type="server"):

    # ==================================================
    # Check if necesarry inputs were given
    # ==================================================
    if not embed_title and not embed:
        raise ValueError("An embed title must be given")

    if not embed_description and not embed:
        raise ValueError("An embed description must be given")

    if not ctx:
        raise ValueError("Context must be given")

    if embed_title:
        embed_title = embed_title.title()

    if cog == None:
        cog = "Main"

    # ==================================================
    # Get the color of the given cog
    # Throw error if it doesnt exist
    # ==================================================
    try:
        color = colors[cog]
    except:
        raise ValueError("A valid cog must be given")

    if data:
        if data_type == "server":
            setJson(f"servers/{ctx.guild.id}", data)
        elif data_type == "user":
            setJson(f"users/{ctx.author.id}", data)
        elif data_type == "hall":
            setJson(f"servers/halls/{ctx.guild.id}", data)

    if embed:
        await ctx.send(embed=embed)
        if log_text:
            log(
                text=log_text,
                cog=cog,
                color=color,
                ctx=ctx
            )
        return

    embed = makeEmbed(
        title=embed_title,
        description=embed_description,
        ctx=ctx
    )
    await ctx.send(embed=embed)
    if log_text:
        log(
            text=log_text,
            cog=cog,
            color=color,
            ctx=ctx
        )
    return


def hexToRGB(hexIn):
    return tuple(int(hexIn[i:i + 2], 16) for i in (0, 2, 4))


def getTime():
    return strftime("%m/%d/%Y %I:%M:%S %p", localtime())


def log(
    text="PLACEHOLDER",
    cog="Main",
    color=None,
    ctx=None,
    event=False):

    if color == None:
        color = colors[cog]

    if ctx:
        if event:
            print("[%s] [%s] [%s] %s [%s] %s %s" % (getTime(), colored("Abacus", "blue"), colored(cog, color), ("." * (10 - len(cog))), ("Direct Message" if not ctx.guild else ctx.guild.name), ("." * (30 - len("Direct Message" if not ctx.guild else ctx.guild.name))), text))
        else:
            print("[%s] [%s] [%s] %s [%s] %s [%s] %s %s" % (getTime(), colored("Abacus", "blue"), colored(cog, color), ("." * (10 - len(cog))), ("Direct Message" if not ctx.guild else ctx.guild.name), ("." * (30 - len("Direct Message" if not ctx.guild else ctx.guild.name))), ctx.author.name, ("." * (20 - len(ctx.author.name))), text))
    else:
        print("[%s] [%s] [%s] %s %s" % (getTime(), colored("Abacus", "blue"), colored(cog, color), ("." * (10 - len(cog))), text))


# Valid Termcolor Colors:
#  - grey
#  - white

#  - green
#  - yellow
#  - blue
#  - cyan
#  - magenta
#  - red
