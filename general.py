import ovalia_auxiliary_protocol as oap
from discord.ext import commands
from importlib import reload
from random import randint, choice
import numpy as np
import discord


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
    @commands.command(brief="Roll a die (1d20 by default)", usage="[die=1d20] [individual_mod=False] [remove=None]", help="Dice rolling, D&D style.\n1d20 means 1 die with 20 sides. 3d6 means 3 dice, each with 6 sides. You can add +[number] to the end to add a modifier (e.g. 2d6+4)\n\nBy default, the modifier is added to the total of all rolls. Use individual_mod=True to apply it to each roll individually.\n\nCross out a number of lowest or highest values, using remove=highest or remove=3lowest.")
    async def roll(self, ctx, die="1d20", *, args=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # Error checking the die amount ==================================================
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

        # Argument parsing ==================================================
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
        
        # Generating rolls ==================================================
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

        # Checking for remove argument ==================================================
        rolls_without_removed = [roll for roll in mod_rolls]
        indexes = np.array([])
        values_removed = []
        if remove_any:
            if remove == "highest":
                # indexes = np.argsort(-mod_rolls)[-remove_amount:]
                indexes = np.argpartition(np.array(mod_rolls), -remove_amount)[-remove_amount:]
                for index in indexes:
                    rolls[index] = f"~~{rolls[index]}~~"
                    values_removed.append(mod_rolls[index])
                    rolls_without_removed.remove(mod_rolls[index])
            elif remove == "lowest":
                # indexes = np.argsort(mod_rolls)[-remove_amount:]
                indexes = np.argpartition(-np.array(mod_rolls), -remove_amount)[-remove_amount:]
                for index in indexes:
                    rolls[index] = f"~~{rolls[index]}~~"
                    values_removed.append(mod_rolls[index])
                    rolls_without_removed.remove(mod_rolls[index])

        total = 0
        for roll in rolls_without_removed: total += roll

        # Output ==================================================
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

        # Error checking for whether they actually gave choices ==================================================
        if choices == "" or len(choices.split(", ")) == 1:
            embed = oap.makeEmbed(title="Whoops!", description="The choose command requires two or more choices, seperated by a comma and a space", ctx=ctx)
            return await ctx.send(embed=embed)
        
        choices = choices.split(", ")
        _choice = choice(choices)
        embed = oap.makeEmbed(title=_choice.title(), description=f"Out of {', '.join(choices[:-1])} and {choices[-1]}, I choose {_choice}", ctx=ctx)
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
            embed = oap.makeEmbed(title="Whoops!", description="Please provide a member\nYou can ping someone as the argument", ctx=ctx)
            return await ctx.send(embed=embed)

        embed = oap.makeEmbed(title=f"Got all info on {user.name}#{user.discriminator}!", description=f"({user.nick})", ctx=ctx)
        embed.add_field(name="ID", value=f"{user.id}", inline=True)
        embed.add_field(name="Created At", value=f"{user.created_at}", inline=True)
        embed.add_field(name="Joined At", value=f"{user.joined_at}", inline=True)
        embed.add_field(name="Roles", value=f"{', '.join([role.name for role in user.roles[1:]])}", inline=True)

        await ctx.send(embed=embed)
        oap.log(text=f"Got info on {user.name}", cog="General", color="cyan", ctx=ctx)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="General", color="cyan")
    bot.add_cog(General(bot))
    reload(oap)
