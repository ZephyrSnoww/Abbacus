import ovalia_auxiliary_protocol as oap
from random import randint, choice
from discord.ext import commands
from importlib import reload
from os import path, listdir
import numpy as np
import discord
import math
import re


class General(commands.Cog, description="General commands, like roll, choose, flip, etc."):
    def __init__(self, bot):
        self.abacus = bot
        self.data = oap.getJson("data")

    # ==================================================
    # Unload event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="General", color="cyan")

    
    # ==================================================
    # Roll command
    # ==================================================
    @commands.command(brief="Roll a die (1d20 by default)", usage="[die=1d20] [individual_mod=False] [remove=None]", help="Dice rolling, D&D style.\n1d20 means 1 die with 20 sides. 3d6 means 3 dice, each with 6 sides. You can add +[number] to the end to add a modifier (e.g. 2d6+4)\n\nBy default, the modifier is added to the total of all rolls. Use individual_mod=True to apply it to each roll individually.\n\nCross out a number of lowest or highest values, using remove=highest or remove=3lowest.\n\nIf you've imported characters with >>import_character, you can roll character-specific die (e.g. \">>roll Brooklynn cha\" or \">>roll Brooklynn per\")\nDo >>list_skills to list all available skills you can roll.\nWhen using this, add \"adv\" or \"dis\" to roll with advantage or disadvantage, and \"save\" to roll a saving throw.")
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
                    mod = oap.mods[character["data"]["abilities"][args.split(" ")[0]]["value"]]

                    # ==================================================
                    # If theyre rolling a saving throw
                    # Add their proficiency bonus (if any)
                    # ==================================================
                    if save:
                        mod += (prof_bonus * character["data"]["abilities"][args.split(" ")[0]]["proficient"])

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
                    mod = oap.mods[character["data"]["abilities"][character["data"]["skills"][args.split(" ")[0]]["ability"]]["value"]]
                    mod += math.floor(prof_bonus * character["data"]["skills"][args.split(" ")[0]]["value"])

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
                embed = oap.makeEmbed(title=output, description=", ".join(rolls), ctx=ctx)
                await ctx.send(embed=embed)
                return oap.log(text=f"Rolled {args.split(' ')[0]} for the character \"{die}\"")


        # ==================================================
        # Error checking for any formatting problems
        # Look for a mod, if nothing, just set it to 0
        # ==================================================
        if True:
            try:
                amount = int(die.split("d")[0])
            except ValueError:
                embed = oap.makeEmbed(title="Whoops!", description="The amount of die must be an integer!", ctx=ctx)
                return await ctx.send(embed=embed)
            try:
                size = int((die.split("d")[1].split("+")[0] if "+" in die else (die.split("d")[1])))
            except ValueError:
                embed = oap.makeEmbed(title="Whoops!", description="The size of the die must be an integer!", ctx=ctx)
                return await ctx.send(embed=embed)
            if "+" in die:
                try:
                    mod = int(die.split("+")[1])
                except ValueError:
                    embed = oap.makeEmbed(title="Whoops!", description="The modifier must be an integer!", ctx=ctx)
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
                embed = oap.makeEmbed(title="Whoops!", description="If you want individual_mod to be true, please use individual_mod=True\n(Check your capitalization!)", ctx=ctx)
                return await ctx.send(embed=embed)
        if "remove=" in args:
            try:
                remove = "highest" if "highest" in args.split("remove=")[1] else ""
                if remove == "": remove = "lowest" if "lowest" in args.split("remove=")[1] else ""
                if remove == "":
                    embed = oap.makeEmbed(title="Whoops!", description="The remove argument must include either \"highest\" or \"lowest\"", ctx=ctx)
                    return await ctx.send(embed=embed)
                remove_amount = int(args.split("remove=")[1].split(remove)[0])
                remove_any = True
            except ValueError:
                if args.split("remove=")[1].split(" ")[0] in ["highest", "lowest"]:
                    remove = args.split("remove=")[1].split(" ")[0]
                    remove_amount = 1
                    remove_any = True
                else:
                    embed = oap.makeEmbed(title="Whoops!", description="The remove argument must include either \"highest\" or \"lowest\"", ctx=ctx)
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
            rolls = [str(roll+mod) + (f" (Natural {roll})" if (roll in [0, 20] and size == 20) else "") for roll in no_mod_rolls]
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
                indexes = np.argpartition(np.array(mod_rolls), -remove_amount)[-remove_amount:]
                for index in indexes:
                    rolls[index] = f"~~{rolls[index]}~~"
                    values_removed.append(mod_rolls[index])
                    rolls_without_removed.remove(mod_rolls[index])
            elif remove == "lowest":
                indexes = np.argpartition(-np.array(mod_rolls), -remove_amount)[-remove_amount:]
                for index in indexes:
                    rolls[index] = f"~~{rolls[index]}~~"
                    values_removed.append(mod_rolls[index])
                    rolls_without_removed.remove(mod_rolls[index])

        # ==================================================
        # Calculate the total
        # ==================================================
        total = 0
        for roll in rolls_without_removed: total += roll

        # ==================================================
        # Send output and log to console
        # ==================================================
        embed = oap.makeEmbed(title=f"Rolled {die}", description=(", ".join(rolls)), ctx=ctx)
        if len(rolls) > 1:
            embed.add_field(name="Total", value=((f"{str(total+mod)}{(f' ({total} without mod)') if mod > 0 else ''}") if not individual_mod else (f"{total}")))
            embed.add_field(name="Average", value=np.mean(rolls_without_removed))
        await ctx.send(embed=embed)
        oap.log(text=f"Rolled {die}", cog="General", color="cyan", ctx=ctx)


    # ==================================================
    # Choose command
    # ==================================================
    @commands.command(brief="Choose between several comma-seperated values", usage="[option one, option two[, option three[, option four]]]", help="Can't decide on something? I'll do it for you!")
    async def choose(self, ctx, *, choices=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # Arg checking
        # ==================================================
        if choices == "" or len(choices.split(", ")) == 1:
            embed = oap.makeEmbed(title="Whoops!", description="The choose command requires two or more choices, seperated by a comma and a space", ctx=ctx)
            return await ctx.send(embed=embed)
        
        # ==================================================
        # Choosing and sending output
        # ==================================================
        choices = choices.split(", ")
        _choice = choice(choices)
        embed = oap.makeEmbed(title=_choice.title() if len(_choice) <= 256 else (_choice.title()[250:] + "..."), description=f"Out of {', '.join(choices[:-1])} and {choices[-1]}, I choose {_choice}", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Made a choice", cog="General", color="cyan", ctx=ctx)


    # ==================================================
    # Flip command
    # ==================================================
    @commands.command(brief="Flip a coin", help="Flip as many coins as you like!")
    async def flip(self, ctx, amount=1):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        try:
            amount = int(amount)
        except ValueError:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter an integer amount of coins to flip", ctx=ctx)
            return await ctx.send(embed=embed)
        choices = ["heads", "tails"]
        out = []
        for i in range(amount):
            out.append(choice(choices))

        embed = oap.makeEmbed(title=f"Flipped {amount} coin{'s' if amount > 1 else ''}!", description=(", ".join(out)) if len(", ".join(out)) <= 2000 else "Flips too big to display!", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Flipped a coin", cog="General", color="cyan", ctx=ctx)


    # ==================================================
    # Whois command
    # ==================================================
    @commands.command(brief="Get info on a user", usage="[ping]", help="Get an in-depth rundown of a user")
    async def whois(self, ctx, user: discord.Member = ""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if user in ["", None]:
            user = ctx.author

        embed = oap.makeEmbed(title=f"Got all info on {user.name}#{user.discriminator}!", description=f"({user.nick})", ctx=ctx)
        embed.add_field(name="ID", value=f"{user.id}", inline=True)
        embed.add_field(name="Created At", value=f"{user.created_at}", inline=True)
        embed.add_field(name="Joined At", value=f"{user.joined_at}", inline=True)
        embed.add_field(name="Roles", value=f"{', '.join([role.name for role in user.roles[1:]])}", inline=True)

        await ctx.send(embed=embed)
        oap.log(text=f"Got info on {user.name}", cog="General", color="cyan", ctx=ctx)


    # ==================================================
    # Poll command
    # ==================================================
    @commands.command(brief="Start a vote on anything you like", usage="[info]", help="Custom emoji can be used - any emoji in the message will be added as a reaction.\nUnfortunately, I can only use emoji that are from the server i'm in.")
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
        emojis = [text.group() for text in re.finditer(r"<:([^\s<>]+):(\d{18})>", input)]
    
        # ==================================================
        # If they didnt enter a poll,
        # And there are <=1 emoji,
        # React with basic yes/no
        # ==================================================
        if input == "" or len(emojis) <= 1:
            if server_data.get("poll"):
                embed = oap.makeEmbed(title=f"Started a Poll", description=("Yes or no?" if input == "" else input), ctx=ctx)
                message = await ctx.send(embed=embed)
                await message.add_reaction((server_data.get("poll").get("yes")) if (server_data.get("poll").get("yes") != "") else "✅")
                await message.add_reaction((server_data.get("poll").get("no")) if server_data.get("poll").get("no") != "" else "❎")
                if "shrug" in input:
                    await message.add_reaction((server_data.get("poll").get("shrug")) if server_data.get("poll").get("shrug") != "" else "🤷")
                return oap.log(text="Made a poll", cog="General", color="cyan", ctx=ctx)
            
            embed = oap.makeEmbed(title=f"Started a Poll", description=("Yes or no?" if input == "" else input), ctx=ctx)
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
        embed = oap.makeEmbed(title=f"Started a Poll", description=input, ctx=ctx)
        message = await ctx.send(embed=embed)
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except:
                await message.delete()
                embed = oap.makeEmbed(title="Whoops!", description=f"I can only use emojis from this sever\n{emoji} isn't from this server", ctx=ctx)
                return await ctx.send(embed=embed)

        # ==================================================
        # Log to console
        # ==================================================
        oap.log(text="Made a poll", cog="General", color="cyan", ctx=ctx)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="General", color="cyan")
    bot.add_cog(General(bot))
    reload(oap)
