from datetime import datetime, timedelta
from time import localtime, strftime
from termcolor import colored
import discord
import json
import math
import os
import re


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
    "Moderation": "red",
    "Games": "cyan",
    "Webserver": "yellow",
    "Stupid": "green"
}


# class

# Converts a 5e ability score to a modifer
def mods(score):
    return math.floor((score - 10) / 2)


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
        author=None,
        image=None,
        thumbnail=None):

    # ==================================================
    # If no color was supplied, use default color
    # ==================================================
    if not color:
        color = 0xffadb6

    # # ==================================================
    # # Make a blank embed
    # # ==================================================
    # _out = discord.Embed()

    # # ==================================================
    # # If a description was supplied
    # # Remove all tabs and extra spaces
    # # Set the description
    # # ==================================================
    # if description != None:
    description = re.sub(r"\t", " ", description)
    while "  " in description:
        description = description.replace("  ", " ")

    # # ==================================================
    # # If a title was supplied
    # # Set it (with .title() for good formatting)
    # # ==================================================
    # if title != None:
    title = title.capitalize()

    # # ==================================================
    # # If a context was given
    # # Get the users color
    # # Set the author of the embed to the author
    # # Set the color to the users color (if it exists)
    # # Set the timestamp (if given)
    # # ==================================================
    # if ctx != None:
    #     user_color = getJson(f"users/{ctx.author.id}").get("color")
    #     _out.set_author(name=ctx.author.nick if ctx.author.nick else ctx.author.name, icon_url=ctx.author.avatar_url)
    #     _out.color = user_color if user_color else color
    #     if timestamp != None:
    #         _out.timestamp = timestamp
    # # ==================================================
    # # Otherwise (no context)
    # # Set the color to default
    # # Set the timstamp (if given)
    # # ==================================================
    # else:
    #     _out.color = color
    #     if timestamp != None:
    #         _out.timestamp = timestamp

    # # ==================================================
    # # If an author was given, change embed author
    # # ==================================================
    # if author != None:
    #     _out.set_author(name=author.nick if author.nick else author.name, icon_url=author.avatar_url)

    # # ==================================================
    # # If an image was given, set the embeds image
    # # ==================================================
    # if image != None:
    #     _out.set_image(url=image)

    # # ==================================================
    # # If a thumbnail was given, set embed thumbnail
    # # ==================================================
    # if thumbnail != None:
    #     _out.set_thumbnail(url=thumbnail)

    if ctx:
        user_color = getJson(f"users/{ctx.author.id}").get("color")
        _out = discord.Embed(title=title, description=description,
                             color=user_color if user_color else color)
    else:
        _out = discord.Embed(title=title, description=description, color=color)

    if author:
        _out.set_author(
            name=author.nick if author.nick else author.name, icon_url=author.avatar_url)
    elif ctx:
        _out.set_author(
            name=ctx.author.nick if ctx.author.nick else ctx.author.name, icon_url=ctx.author.avatar_url)

    if image:
        _out.set_image(url=image)
    if thumbnail:
        _out.set_thumbnail(url=thumbnail)

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
        embed_image=None,
        embed=None,
        log_text=None,
        cog=None,
        ctx=None,
        data=None,
        data_type="server"):

    # ==================================================
    # Check if necesarry inputs were given
    # ==================================================
    # if not embed_title and not embed:
    #     raise ValueError("An embed title must be given")

    # if not embed_description and not embed:
    #     raise ValueError("An embed description must be given")

    if not ctx:
        raise ValueError("Context must be given")

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
        image=embed_image,
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
        event=False,
        payload=False,
        guild=None,
        author=None):

    if color == None:
        color = colors[cog]

    if payload:
        guild = "Direct Message" if not guild else guild.name
        author = author.name
    elif ctx:
        guild = "Direct Message" if not ctx.guild else ctx.guild.name
        author = ctx.author.name

    if ctx or payload:
        if event:
            print(f"[{getTime()}] [{colored('Abacus', 'blue')}] [{colored(cog, color)}] {'.' * (14-len(cog))} [{guild}] {'.' * (30-len(guild))} {text}")
        else:
            print(f"[{getTime()}] [{colored('Abacus', 'blue')}] [{colored(cog, color)}] {'.' * (14-len(cog))} [{guild}] {'.' * (30-len(guild))} [{author}] {'.' * (20-len(author))} {text}")
    else:
        print(f"[{getTime()}] [{colored('Abacus', 'blue')}] [{colored(cog, color)}] {'.' * (14-len(cog))} {text}")


# Valid Termcolor Colors:
#  - grey
#  - white

#  - green
#  - yellow
#  - blue
#  - cyan
#  - magenta
#  - red
