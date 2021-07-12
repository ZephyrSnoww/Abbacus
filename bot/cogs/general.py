from datetime import datetime, timedelta
import ovalia_auxiliary_protocol as oap
from random import randint, choice
from discord.ext import commands
from importlib import reload
from os import path, listdir
import requests as r
import numpy as np
import emoji as em
import discord
import asyncio
import numexpr
import nasapy
import math
import re


class General(commands.Cog, description="General commands, like roll, choose, flip, etc."):
    def __init__(self, bot):
        self.abacus = bot
        self.data = oap.getJson("data")
        self.nasa_key = ""
        self.nasa = nasapy.Nasa(key=self.nasa_key)
        self.cog_name = "General"

    # ==================================================
    # Unload event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="General", color="cyan")

    # ==================================================
    # Roll command
    # ==================================================

    @commands.command(brief="Roll a die (1d20 by default)", usage="[die]", help="""\
        __**Dice rolling, D&D style**__
        - 1d20 means 1 die with 20 sides. 3d6 means 3 dice, each with 6 sides.
        `>>roll 1d20`
        
        __**Modifiers**__
        - You can add +[number] to the end to add a modifier.
        `>>roll 1d20+4`
        
        __**Individually Adding Modifiers**__
        - By default, the modifier is added to the total of all rolls.
        - Use individual_mod=True to apply it to each roll individually.
        `>>roll 4d20+4 individual_mod=True`
        
        __**Removing High or Low Rolls**__
        - Cross out a number of lowest or highest values, using remove=highest or remove=3lowest.
        `>>roll 5d20 remove=2lowest`
        
        __**Rolling Using Characters**__
        - If you've imported characters with >>import_character, you can roll character-specific die.
        - Do `>>list_skills` to list all available skills you can roll.
        - When using this, add \"adv\" or \"dis\" to roll with advantage or disadvantage
        - When using this, add \"save\" to roll a saving throw.
        `>>roll Brooklyn acr`
        `>>roll Avi ste adv`
        `>>roll Itova dec save`
        `>>roll Acdern ins save adv`""")
    async def roll(self, ctx, die="1d20", *, args=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # If the author has characters imported
        # If the "die" arg is the name of a character
        # ==================================================
        if path.exists(f"characters/{ctx.author.id}"):
            if die in [file[:-5] for file in listdir(f"characters/{ctx.author.id}")]:
                # ==================================================
                # Get the characters stats
                # Initialize various misc variables
                # ==================================================
                character = oap.getJson(f"characters/{ctx.author.id}/{die}")
                advantage = False
                disadvantage = False
                save = False
                prof_bonus = 0

                if character["data"]["attributes"].get("prof"):
                    prof_bonus = character["data"]["attributes"]["prof"]

                if "adv" in args.split(" "):
                    advantage = True
                if "dis" in args.split(" "):
                    disadvantage = True
                if "save" in args.split(" "):
                    save = True

                # ==================================================
                # If theyre rolling a flat ability check
                # ==================================================
                if args.split(" ")[0] in list(oap.abilities.keys()):
                    # ==================================================
                    # Get their ability mod
                    # Check for advantage/disadvantage/save
                    # ==================================================
                    mod = oap.mods(
                        character["data"]["abilities"][args.split(" ")[0]]["value"])

                    # ==================================================
                    # If theyre rolling a saving throw
                    # Add their proficiency bonus (if any)
                    # ==================================================
                    if save:
                        mod += (prof_bonus * character["data"]
                                ["abilities"][args.split(" ")[0]]["proficient"])

                    # ==================================================
                    # Make the output string
                    # ==================================================
                    output = f"{oap.abilities[args.split(' ')[0]]} {'Save' if save else 'Roll'} (+{mod}) for {die}{f' (Advantage)' if advantage else (' (Disadvantage)' if disadvantage else '')}"

                # ==================================================
                # If theyre rolling a skill
                # ==================================================
                elif args.split(" ")[0] in list(oap.skills.keys()):
                    # ==================================================
                    # Get their base skill mod
                    # Then add proficiency bonus, if theyre proficient
                    # ==================================================
                    mod = oap.mods(character["data"]["abilities"][character["data"]["skills"][args.split(
                        " ")[0]]["ability"]]["value"])
                    mod += math.floor(prof_bonus *
                                      character["data"]["skills"][args.split(" ")[0]]["value"])

                    output = f"{oap.skills[args.split(' ')[0]]} ({oap.abilities[character['data']['skills'][args.split(' ')[0]]['ability']]}) {'Save' if save else 'Roll'} (+{mod}) for {die}{f' (Advantage)' if advantage else (' (Disadvantage)' if disadvantage else '')}"

                # ==================================================
                # If rolling with advantage or disadvantage
                # Roll twice
                # Otherwise just roll once
                # ==================================================
                if advantage or disadvantage:
                    base_rolls = [randint(1, 20), randint(1, 20)]
                else:
                    base_rolls = [randint(1, 20)]

                # ==================================================
                # Add their modifier to the rolls
                # ==================================================
                rolls = [
                    f"{roll + mod}{f' (natural {roll})' if roll in [1, 20] else ''}" for roll in base_rolls]

                # ==================================================
                # Send output
                # Log to console
                # ==================================================
                embed = oap.makeEmbed(
                    title=output, description=", ".join(rolls), ctx=ctx)
                await ctx.send(embed=embed)
                return oap.log(text=f"Rolled {args.split(' ')[0]} for the character \"{die}\"", cog=self.cog_name, ctx=ctx)

        # ==================================================
        # Error checking for any formatting problems
        # Look for a mod, if nothing, just set it to 0
        # ==================================================
        if True:
            try:
                amount = int(die.split("d")[0])
            except ValueError:
                embed = oap.makeEmbed(
                    title="Whoops!", description="The amount of die must be an integer!", ctx=ctx)
                return await ctx.send(embed=embed)
            try:
                size = int((die.split("d")[1].split(
                    "+")[0] if "+" in die else (die.split("d")[1])))
            except ValueError:
                embed = oap.makeEmbed(
                    title="Whoops!", description="The size of the die must be an integer!", ctx=ctx)
                return await ctx.send(embed=embed)
            if "+" in die:
                try:
                    mod = int(die.split("+")[1])
                except ValueError:
                    embed = oap.makeEmbed(
                        title="Whoops!", description="The modifier must be an integer!", ctx=ctx)
                    return await ctx.send(embed=embed)
            else:
                mod = 0

        # ==================================================
        # Arg checking
        # ==================================================
        individual_mod = False
        remove_any = False
        if "individual_mod=" in args:
            if args.split("individual_mod=")[1].split(" ")[0] == "True":
                individual_mod = True
            else:
                embed = oap.makeEmbed(
                    title="Whoops!", description="If you want individual_mod to be true, please use individual_mod=True\n(Check your capitalization!)", ctx=ctx)
                return await ctx.send(embed=embed)
        if "remove=" in args:
            try:
                remove = "highest" if "highest" in args.split("remove=")[
                    1] else ""
                if remove == "":
                    remove = "lowest" if "lowest" in args.split("remove=")[
                        1] else ""
                if remove == "":
                    embed = oap.makeEmbed(
                        title="Whoops!", description="The remove argument must include either \"highest\" or \"lowest\"", ctx=ctx)
                    return await ctx.send(embed=embed)
                remove_amount = int(args.split("remove=")[1].split(remove)[0])
                remove_any = True
            except ValueError:
                if args.split("remove=")[1].split(" ")[0] in ["highest", "lowest"]:
                    remove = args.split("remove=")[1].split(" ")[0]
                    remove_amount = 1
                    remove_any = True
                else:
                    embed = oap.makeEmbed(
                        title="Whoops!", description="The remove argument must include either \"highest\" or \"lowest\"", ctx=ctx)
                    return await ctx.send(embed=embed)

        # ==================================================
        # Generating rolls, checking for individual mod
        # ==================================================
        rolls = [randint(1, size) for i in range(amount)]
        if len(rolls) == 1:
            individual_mod = True
        if individual_mod:
            no_mod_rolls = rolls
            mod_rolls = [roll+mod for roll in rolls]
            rolls = [str(roll+mod) + (f" (Natural {roll})" if (
                roll in [0, 20] and size == 20) else "") for roll in no_mod_rolls]
        else:
            mod_rolls = rolls
            rolls = [str(roll) for roll in mod_rolls]

        # ==================================================
        # Checking and handling the remove argument
        # ==================================================
        rolls_without_removed = [roll for roll in mod_rolls]
        indexes = np.array([])
        values_removed = []
        if remove_any:
            if remove == "highest":
                indexes = np.argpartition(
                    np.array(mod_rolls), -remove_amount)[-remove_amount:]
                for index in indexes:
                    rolls[index] = f"~~{rolls[index]}~~"
                    values_removed.append(mod_rolls[index])
                    rolls_without_removed.remove(mod_rolls[index])
            elif remove == "lowest":
                indexes = np.argpartition(-np.array(mod_rolls), -
                                          remove_amount)[-remove_amount:]
                for index in indexes:
                    rolls[index] = f"~~{rolls[index]}~~"
                    values_removed.append(mod_rolls[index])
                    rolls_without_removed.remove(mod_rolls[index])

        # ==================================================
        # Calculate the total
        # ==================================================
        total = 0
        for roll in rolls_without_removed:
            total += roll

        # ==================================================
        # Send output and log to console
        # ==================================================
        # if die == "1d6":
        #     embed = oap.makeEmbed(
        #         title=f"Rolled {die}",
        #         description=f"",
        #         ctx=ctx
        #     )

        #     return oap.log(
        #         text=f"Rolled {die}",
        #         cog=self.cog_name,
        #         ctx=ctx
        #     )

        embed = oap.makeEmbed(
            title=f"Rolled {die}", description=(", ".join(rolls)), ctx=ctx)
        if len(rolls) > 1:
            embed.add_field(name="Total", value=(
                (f"{str(total+mod)}{(f' ({total} without mod)') if mod > 0 else ''}") if not individual_mod else (f"{total}")))
            embed.add_field(name="Average", value=np.mean(
                rolls_without_removed))
        await ctx.send(embed=embed)
        oap.log(text=f"Rolled {die}", cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # Choose command
    # ==================================================

    @commands.command(brief="Choose between comma-seperated values", usage="[option one, option two[, option three]]", help="I'll choose between any options you supply. Each option must be separated by a command and a space.\n\n__**Examples**__\n`>>choose option one, option two, option three`")
    async def choose(self, ctx, *, choices=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # Arg checking
        # ==================================================
        if choices == "" or len(choices.split(", ")) == 1:
            embed = oap.makeEmbed(
                title="Whoops!", description="The choose command requires two or more choices, seperated by a comma and a space", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Choosing and sending output
        # ==================================================
        choices = choices.split(", ")
        _choice = choice(choices)
        embed = oap.makeEmbed(title=_choice.title() if len(_choice) <= 256 else (_choice.title()[
                              250:] + "..."), description=f"Out of {', '.join(choices[:-1])} and {choices[-1]}, I choose {_choice}", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Made a choice", cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # Flip command
    # ==================================================

    @commands.command(brief="Flip a coin", help="Flip as many coins as you like! Input an amount of coins to change how many to flip.\n\n__**Examples**__\n`>>flip`\n`>>flip 50`")
    async def flip(self, ctx, amount=1):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        try:
            amount = int(amount)
        except ValueError:
            embed = oap.makeEmbed(
                title="Whoops!", description="Please enter an integer amount of coins to flip", ctx=ctx)
            return await ctx.send(embed=embed)
        choices = ["heads", "tails"]
        out = []
        for i in range(amount):
            out.append(choice(choices))

        embed = oap.makeEmbed(title=f"Flipped {amount} coin{'s' if amount > 1 else ''}!", description=(
            ", ".join(out)) if len(", ".join(out)) <= 2000 else "Flips too big to display!", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Flipped a coin", cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # Whois command
    # ==================================================

    @commands.command(brief="Get info on a user", usage="[ping]", help="Get an in-depth rundown of a user by pinging them with this command.\n\n__**Examples**__\n`>>whios @toaster`")
    async def whois(self, ctx, user: discord.Member = ""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if user in ["", None]:
            user = ctx.author

        embed = oap.makeEmbed(
            title=f"Got all info on {user.name}#{user.discriminator}!", description=f"({user.nick})", ctx=ctx)
        embed.add_field(name="ID", value=f"{user.id}", inline=True)
        embed.add_field(name="Created At",
                        value=f"{user.created_at}", inline=True)
        embed.add_field(name="Joined At",
                        value=f"{user.joined_at}", inline=True)
        embed.add_field(
            name="Roles", value=f"{', '.join([role.name for role in user.roles[1:]])}", inline=True)

        await ctx.send(embed=embed)
        oap.log(text=f"Got info on {user.name}",
                cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # Poll command
    # ==================================================

    @commands.command(brief="Start a vote on anything you like", usage="[info]", help="Create a poll! Custom emoji can be used - any emoji in the message will be added as a reaction.\nUnfortunately, I can only use emoji that are from the server I'm in.\n\n__**Examples**__\n>>poll Should I buy a donut?\n>>poll :green_heart: :purple_heart:\n>>poll What should we do?\n:movie_camera: watch a movie\n:video_game: play a video game\n:chess_pawn: play a board game")
    async def poll(self, ctx, *, input=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("poll"):
            if server_data.get("poll").get("delete_invocation"):
                await oap.tryDelete(ctx)
            elif server_data.get("poll").get("delete_invocation") == None:
                await oap.tryDelete(ctx)
        else:
            await oap.tryDelete(ctx)

        # ==================================================
        # Get all emoji in the message
        # ==================================================
        emojis = [text.group() for text in re.finditer(
            r"(:([^\s:]+):(?!\d))|(<(:|(a:))([^\s<>]+):(\d{18})>)", em.demojize(input))]

        for i in range(len(emojis)):
            if "<" not in emojis[i]:
                temp = emojis[i]
                emojis[i] = (em.emojize(temp))

        # ==================================================
        # If they didnt enter a poll,
        # And there are <=1 emoji,
        # React with basic yes/no
        # ==================================================
        if input == "" or len(emojis) <= 1:
            if server_data.get("poll"):
                embed = oap.makeEmbed(title=f"Started a Poll", description=(
                    "Yes or no?" if input == "" else input), ctx=ctx)
                message = await ctx.send(embed=embed)
                await message.add_reaction((server_data.get("poll").get("yes")) if (server_data.get("poll").get("yes") != "") else "✅")
                await message.add_reaction((server_data.get("poll").get("no")) if server_data.get("poll").get("no") != "" else "❎")
                if "shrug" in input:
                    await message.add_reaction((server_data.get("poll").get("shrug")) if server_data.get("poll").get("shrug") != "" else "🤷")
                return oap.log(text="Made a poll", cog="General", color="cyan", ctx=ctx)

            embed = oap.makeEmbed(title=f"Started a Poll", description=(
                "Yes or no?" if input == "" else input), ctx=ctx)
            message = await ctx.send(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❎")
            if "shrug" in input:
                await message.add_reaction("🤷")
            return oap.log(text="Made a poll", cog="General", color="cyan", ctx=ctx)

        # ==================================================
        # If they did enter stuff, and there are >1 emoji
        # React with each emoji
        # ==================================================
        embed = oap.makeEmbed(title=f"Started a Poll",
                              description=input, ctx=ctx)
        message = await ctx.send(embed=embed)
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except:
                await message.delete()
                embed = oap.makeEmbed(
                    title="Whoops!", description=f"I can only use emojis from this sever\n{emoji} isn't from this server", ctx=ctx)
                return await ctx.send(embed=embed)

        # ==================================================
        # Log to console
        # ==================================================
        oap.log(text="Made a poll", cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # Time until command
    # ==================================================

    @commands.command(brief="Get the time until some given time", usage="[time]", help="I'll calculate the time until a date in the future or past for you!\nTimes are formatted as hour:minute:second, and dates are formatted as day/month/year.\n\n__**Examples**__\n`>>time_until 14:30`\n`>>time_until 04/04/2073`", aliases=["t-minus"])
    async def time_until(self, ctx, date=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # Arg error checking
        # ==================================================
        if date == "":
            embed = oap.makeEmbed(
                title="Whoops!", description="Please enter a date", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # If the date has a colon
        # (its a time)
        # ==================================================
        if ":" in date:
            date = date + " " + datetime.now().strftime("%d/%m/%Y")
            try:
                date_obj = datetime.strptime(date, "%H:%M %d/%m/%Y")
            except ValueError:
                try:
                    date_obj = datetime.strptime(date, "%H:%M:%S %d/%m/%Y")
                except ValueError:
                    embed = oap.makeEmbed(
                        title="Whoops!", description="That wasnt a valid time format\nEnter a time (Hour:Minute, like 16:30) or date (Day/Month/Year, like 3/4/21)", ctx=ctx)
                    return await ctx.send(embed=embed)

            difference = (date_obj - datetime.now()).total_seconds()
            diff_type = "There are (difference) seconds to go until (time)"
            if difference >= 3600:
                difference /= 60
                difference /= 60
                diff_type = "There are (difference) hours to go until (time)"
            elif difference >= 60:
                difference /= 60
                diff_type = "There are (difference) minutes to go until (time)"
            elif difference == 0:
                diff_type = "It is currently (time)"
            elif difference > -60:
                diff_type = "(time) happened (difference) seconds ago"
            elif difference > -3600:
                difference /= 60
                diff_type = "(time) happened (difference) minutes ago"
            else:
                difference /= 60
                difference /= 60
                diff_type = "(time) happened (difference) hours ago"

            difference = math.ceil(difference)

            if difference == 1:
                diff_type = diff_type.replace("are", "is")
                diff_type = diff_type.replace("seconds", "second")
                diff_type = diff_type.replace("minutes", "minute")
                diff_type = diff_type.replace("hours", "hour")

            if difference < 0:
                difference = -difference

            time_string = date_obj.strftime("%H:%M:%S")
            diff_type = diff_type.replace("(difference)", str(difference))
            diff_type = diff_type.replace("(time)", time_string)

        # ==================================================
        # If the date had a slash
        # (its a date)
        # ==================================================
        elif "/" in date:
            try:
                date_obj = datetime.strptime(date, "%d/%m/%Y")
            except ValueError:
                embed = oap.makeEmbed(
                    title="Whoops!", description="That wasnt a valid time format\nEnter a time (Hour:Minute, like 16:30) or date (Day/Month/Year, like 03/04/2021)", ctx=ctx)
                return await ctx.send(embed=embed)

            difference = math.ceil(
                (date_obj - datetime.now()).total_seconds() / 86400)
            diff_type = "There are (difference) days to go until (time)"
            if difference >= 365:
                difference /= 365
                diff_type = "There are (difference) years to go until (time)"
            elif difference == 0:
                diff_type = "It is currently (time)"
            elif difference > -365 and difference < 0:
                diff_type = "(time) happened (difference) days ago"
            elif difference <= -365:
                difference /= 365
                diff_type = "(time) happened (difference) years ago"

            difference = math.ceil(difference)

            if difference == 1:
                diff_type = diff_type.replace("are", "is")
                diff_type = diff_type.replace("days", "day")
                diff_type = diff_type.replace("years", "year")

            if difference < 0:
                difference = -difference

            time_string = date_obj.strftime("%d/%m/%Y")
            diff_type = diff_type.replace("(difference)", str(difference))
            diff_type = diff_type.replace("(time)", time_string)

        else:
            embed = oap.makeEmbed(
                title="Whoops!", description="That wasnt a valid time format\nEnter a time (Hour:Minute, like 16:30) or date (Day/Month/Year, like 03/04/2021)", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Send output
        # Log to console
        # ==================================================
        embed = oap.makeEmbed(title="Here You Go!",
                              description=diff_type, ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(
            text=f"Got the time until {time_string}", cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # NASA
    # ==================================================

    @commands.command(brief="", usage="", help="", enabled=False)
    async def nasa(self, ctx, *, args=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if args == "":
            return await ctx.send(self.nasa.picture_of_the_day()["hdurl"])

        if args == "exoplanets":
            return await ctx.send(str(nasapy.exoplanets())[:2000])

        if args == "epic":
            return await ctx.send(str(self.nasa.epic(date=(datetime.now() - timedelta(2))))[:2000])

        if args.split(" ")[0] == "search":
            return await ctx.send(str(re.sub(r' ', '%20', "\n".join(r.get(url=(nasapy.media_search(query=args[6:])["items"])[0]["href"]).json())))[:2000])

        # image = self.nasa.earth_imagery(lat=float(args.split(" ")[0]), lon=float(args.split(" ")[1]), date=datetime.now() - timedelta(days=365))
        req = r.get(url="https://api.nasa.gov/planetary/earth/imagery/", params={
            "lon": float(args.split(" ")[1]),
            "lat": float(args.split(" ")[0]),
            "dim": float(args.split(" ")[2]),
            "date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "cloud_score": False,
            "api_key": self.nasa_key
        }, headers={'accept': 'application/json'})
        with open("images/nasa.png", "wb") as file:
            file.write(req.content)
        await ctx.send(file=discord.File("images/nasa.png"))

        # embed = oap.makeEmbed(title="PLACEHOLDER", description="PLACEHOLDER", ctx=ctx)
        # await ctx.send(embed=embed)
        # oap.log(text="PLACEHOLDER", cog="PLACEHOLDER", color="PLACEHOLDER", ctx=ctx)

    # ==================================================
    # Math
    # ==================================================

    @commands.command(brief="Calculate some math", usage="[math]", help="I can do math for you!\nIf you want to use exponents, such as 2^2, you must do 2\*\*2.\n\n__**Examples**__\n`>>math 2+2`\n`>>math 7-3`\n`>>math 15/3`\n`>>math 12**12`")
    async def math(self, ctx, *, input=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if input == "":
            embed = oap.makeEmbed(
                title="Whoops!", description="Please enter a formula", ctx=ctx)
            return await ctx.send(embed=embed)

        output = str(numexpr.evaluate(input).item())

        embed = oap.makeEmbed(title="Here You Go!",
                              description=output, ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Did some math", cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # Queue
    # ==================================================

    @commands.command(brief="", usage="", help="")
    async def queue(self, ctx, time="", *, message=""):
        await oap.tryDelete(ctx)

        if time == "":
            return await oap.give_output(
                embed_title="Whoops!",
                embed_description="Please enter a time you wish to wait before sending the message!",
                cog=self.cog_name,
                log_text="Tried to queue a message without a time",
                ctx=ctx
            )

        if message == "" and len(ctx.message.attachments) == 0:
            return await oap.give_output(
                embed_title="Whoops!",
                embed_description="Please enter a message, or attach an image youd like me to send!",
                cog=self.cog_name,
                log_text="Tried to queue a message without a message",
                ctx=ctx
            )

        time = re.split(r"(\D)", time)
        time = time[:-1]
        wait_time = 0

        for i in range(int(len(time) / 2)):
            x = i * 2
            try:
                wait_time += int(time[x]) * (1 if time[x+1] == "s" else (60 if time[x+1] == "m" else (
                    60 * 60 if time[x+1] == "h" else (60 * 60 * 24 if time[x+1] == "d" else 1))))
            except:
                return await oap.give_output(
                    embed_title="Whoops!",
                    embed_description="Please enter a valid time!",
                    cog=self.cog_name,
                    log_text="Tried to queue a message without a valid time",
                    ctx=ctx
                )

        if wait_time == 0:
            return await oap.give_output(
                embed_title="Whoops!",
                embed_description="Please enter a valid time!",
                cog=self.cog_name,
                log_text="Tried to queue a message without a valid time",
                ctx=ctx
            )

        await asyncio.sleep(wait_time)

        channel_webhooks = await ctx.channel.webhooks()
        has_webhook = False

        for _webhook in channel_webhooks:
            if _webhook.user.name == self.abacus.user.name:
                has_webhook = True
                webhook = _webhook

        if not has_webhook:
            webhook = await ctx.channel.create_webhook(name="Placement Webhook")

        if message == "":
            try:
                await webhook.send("\n".join([attachment.url for attachment in ctx.message.attachments]), username=ctx.author.name, avatar_url=ctx.author.avatar_url, wait=True)
            except:
                await ctx.send("\n".join([attachment.url for attachment in ctx.message.attachments]))
        else:
            try:
                await webhook.send(message + "\n\n" + "\n".join([attachment.url for attachment in ctx.message.attachments]), username=ctx.author.name, avatar_url=ctx.author.avatar_url, wait=True)
            except:
                await ctx.send(message + "\n\n" + "\n".join([attachment.url for attachment in ctx.message.attachments]))

    # ==================================================
    # Invite
    # ==================================================

    @commands.command(brief="Get my invite link", usage="", help="Want to add me to your server? This makes it easy for you!\n\n__**Examples**__\n`>>invite`")
    async def invite(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        embed = oap.makeEmbed(title="Here's My Invite Link!",
                              description="https://discord.com/api/oauth2/authorize?client_id=681498257284661258&permissions=8&scope=bot", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Got an invite link",
                cog="General", color="cyan", ctx=ctx)

    # ==================================================
    # Help command
    # ==================================================

    @commands.command(brief="", usage="", help="", hidden=True)
    async def help(self, ctx, _in=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # If they want general help
        # Make a base embed
        # ==================================================
        if _in == "all" or _in == "":
            embed = oap.makeEmbed(title="Here are all of my cogs and commands".title(
            ), description="`>>help [command]` for more detailed information.", ctx=ctx)

            # ==================================================
            # Add each cog as a field
            # List each command in the cog's field
            # ==================================================
            for cog in self.abacus.cogs:
                if cog not in ["Events", "Webserver"]:
                    cog_commands = self.abacus.cogs[cog].walk_commands()
                    valid_commands = list(
                        filter(lambda c: (c.enabled == True and c.hidden == False), cog_commands))
                    embed.add_field(name=f"__**{cog}**__", value=("\n".join(
                        [f"**>>{command.name}** - {command.short_doc}" for command in valid_commands])), inline=False)

            # ==================================================
            # Send the message
            # Log to console
            # ==================================================
            await ctx.send(embed=embed)
            return oap.log(text="Got general help (test)", cog="General", color="cyan", ctx=ctx)

        # ==================================================
        # If they entered a command
        # ==================================================
        if _in in [command.name for command in self.abacus.commands]:
            command = self.abacus.get_command(_in)
            embed = oap.makeEmbed(
                title=f"The {command.name} Command", description=f"{command.help}", ctx=ctx)

            await ctx.send(embed=embed)
            return oap.log(text=f"Got help for the {command.name} command", cog="General", color="cyan", ctx=ctx)

        # ==================================================
        # If they didnt enter anything
        # Ask for a category
        # ==================================================

        linebreak = "\n"
        embed = oap.makeEmbed(title="Alright!",
                              # __**Hey, I'm Abacus!**__
                              # I'm a general purpose discord bot written by programming hobbyist {self.abacus.owner.mention}! I'm basically always in progress, so if your favorite command starts giving you errors, don't worry! Usually, {self.abacus.owner.mention} will have it fixed pretty quickly!

                              # __**Almost everything I do is disabled by default**__
                              # I do a lot of things, which makes me a bit hard to manage sometimes. To make it easier on you, I disable most things for any new server I join. Don't worry! You can enable them with `>>toggle`

                              # __**Need Help? Have a Suggestion?**__
                              # Feel free to join my support server!

                              description=f"""\
                Send a message with the category you want help with.
            
                __**Valid Categories**__
                {linebreak.join([f'- {cog}' for cog in self.abacus.cogs])}
            """, ctx=ctx)
        cog_request_message = await ctx.send(embed=embed)

        def check(message):
            return message.author.id == ctx.author.id

        wanted_cog_message = await self.abacus.wait_for("message", check=check)
        wanted_cog = wanted_cog_message.content.lower()

        # ==================================================
        # If they didnt enter a valid cog
        # Send an error
        # ==================================================
        if wanted_cog not in [cog.lower() for cog in self.abacus.cogs]:
            embed = oap.makeEmbed(
                title="Whoops!", description="I couldn't find a cog with that name.\nTry the command again!", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Get all comands from the cog
        # ==================================================
        cog = wanted_cog.title()
        if cog == "Dnd":
            cog = "DND"
        commands = self.abacus.cogs[cog].walk_commands()
        valid_commands = list(
            filter(lambda c: (c.enabled == True and c.hidden == False), commands))

        # ==================================================
        # Send an embed with all commands in the cog
        # Then listen for any input
        # ==================================================
        embed = oap.makeEmbed(title=f"The {cog} Cog", description=("*Follow this up with the name of a command, and I'll give you more detailed help!*\n\n" + "\n".join(
            [f"**>>{command.name}** - {command.short_doc}" for command in valid_commands])), ctx=ctx)
        command_list_message = await ctx.send(embed=embed)
        wanted_command_message = await self.abacus.wait_for("message", check=check)
        wanted_command = wanted_command_message.content.lower()

        # ==================================================
        # If they follow it up with a command name
        # Give them detailed help on that command
        # ==================================================
        if wanted_command in [command.name for command in self.abacus.commands]:
            command = self.abacus.get_command(wanted_command)
            embed = oap.makeEmbed(
                title=f"The {command.name.title()} Command", description=f"{command.help}", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text=f"Got help for the {command.name} command", cog="General", color="cyan", ctx=ctx)

        # ==================================================
        # Otherwise just ignore it and log to console
        # ==================================================
        return oap.log(text=f"Got help for the {cog} cog", cog="General", color="cyan", ctx=ctx)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="General", color="cyan")
    bot.add_cog(General(bot))
    reload(oap)
