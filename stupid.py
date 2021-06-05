import ovalia_auxiliary_protocol as oap
from discord.ext import commands
from importlib import reload
from aiohttp import web
from os import listdir
from random import *
import requests
import asyncio
import discord
import inspect
import json
import re


class Stupid(commands.Cog, description="literally nothing"):
    def __init__(self, bot):
        self.abacus = bot
        self.cog_name = "Stupid"
        self.data = oap.getJson("data")

    # ==================================================
    # Unload Event
    # ==================================================
    def cog_unload(self):
        asyncio.ensure_future(self.site.stop())
        oap.log(text="Unloaded", cog=self.cog_name)
















    # ==================================================
    # Joining the chaos
    # ==================================================
    @commands.command()
    async def join(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if not server_data.get("joinees"):
            server_data["joinees"] = {}

        # ==================================================
        # If theyre already joined
        # Dont add them
        # ==================================================
        if str(ctx.author.id) in [key for key, value in server_data["joinees"].items()]:
            return await oap.give_output(
                embed_title="Nice try",
                embed_description="You're already trapped here",
                log_text="Tried to join again",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        # ==================================================
        # Add them so the joinee list
        # ==================================================
        server_data["joinees"][ctx.author.id] = {
            "user_id": ctx.author.id,
            "value": 100
        }

        # ==================================================
        # Give output
        # ==================================================
        return await oap.give_output(
            embed_title="Alright fucko",
            embed_description="I've added you to the hellhole",
            log_text="Joined",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )



















    # ==================================================
    # Leave
    # ==================================================
    @commands.command()
    async def leave(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if not server_data.get("joinees"):
            server_data["joinees"] = {}

        if str(ctx.author.id) in [key for key, value in server_data["joinees"].items()]:
            return await oap.give_output(
                embed_title="Oh, you thought you could leave?",
                embed_description="You're stuck here forever lol",
                log_text="Tried to leave",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        return await oap.give_output(
            embed_title="You haven't joined",
            embed_description="You're one of the lucky few",
            log_text="Tried to leave but hadnt joined",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )


















    @commands.command()
    async def what(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if not server_data.get("joinees"):
            server_data["joinees"] = {}

        if str(ctx.author.id) in [key for key, value in server_data["joinees"].items()]:
            return await oap.give_output(
                embed_title="Hm?",
                embed_description=f"""\
                    Oh, you want me to explain this to you?
                    *fine.*

                    You have value. You're worth exactly {server_data["joinees"][str(ctx.author.id)]["value"]}, actually.

                    There's nothing gained by adding value to your person. Only bragging rights.

                    If you hit 0 value, you die. I'll kick you from this server. Unfortunately, the gods that be have probably provided an invite link, so you'll be able to join back in no time. but whatever.

                    Gamble points with `>>gamble`
                    Steal from someone with `>>steal`
                    """,
                log_text="Got help",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        return await oap.give_output(
            embed_title="You haven't succumbed",
            embed_description="You can't ask for help until you need it",
            log_text="Tried to get help",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )





















    @commands.command()
    async def bal(self, ctx, person:discord.Member=None):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if not server_data.get("joinees"):
            server_data["joinees"] = {}

        if str(ctx.author.id) in [key for key, value in server_data["joinees"].items()]:
            if person:
                if str(person.id) in [key for key, value in server_data["joinees"].items()]:
                    return await oap.give_output(
                        embed_title="Measuring self-worth in currency, I like it",
                        embed_description=f"They're worth {server_data['joinees'][str(person.id)]['value']}",
                        log_text="Got their value",
                        cog=self.cog_name,
                        ctx=ctx,
                        data=server_data
                    )

                return await oap.give_output(
                    embed_title="They haven't committed sin",
                    embed_description=f"Get them to `>>join` before doing anything to them",
                    log_text="Tried to get the value of someone not joined",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            return await oap.give_output(
                embed_title="Measuring self-worth in currency, I like it",
                embed_description=f"You're worth {server_data['joinees'][str(ctx.author.id)]['value']}",
                log_text="Got their value",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        return await oap.give_output(
            embed_title="You haven't been dragged into hell yet",
            embed_description=f"`>>join` the circus to have and get value",
            log_text="Tried to get their value",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )




















    @commands.command()
    async def gamble(self, ctx, amount=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if not server_data.get("joinees"):
            server_data["joinees"] = {}



        if str(ctx.author.id) in [key for key, value in server_data["joinees"].items()]:
            if amount == "":
                return await oap.give_output(
                    embed_title="You hafta give an amount to gamble",
                    embed_description=f"Otherwise what would be at risk?",
                    log_text="Tried to gamble nothing",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            try:
                amount = int(amount)
            except:
                return await oap.give_output(
                    embed_title="You must give a number as how much you want to gamble",
                    embed_description=f"I don't take material posessions, only meaningless measures of self-worth",
                    log_text="Tried to gamble a material posession",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            if amount > server_data["joinees"][str(ctx.author.id)]["value"]:
                return await oap.give_output(
                    embed_title="You can't gamble more than you have",
                    embed_description=f"Sorry bud, you can't go into crippling debt here",
                    log_text="Tried to gamble more than they have",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            roll = randint(0, 100)



            if roll == 0:
                title = "Holy fuck"
                description = "You just lost quadruple what you gambled.\nHow did you even do that"
                server_data["joinees"][str(ctx.author.id)]["value"] -= amount*4
            elif roll == 99:
                title = "What"
                description = "Goddamn you just won quadruple what you gambled.\nAre you cheating???"
                server_data["joinees"][str(ctx.author.id)]["value"] += amount*3
            elif roll > 80:
                title = "Alright, cool"
                description = "You just doubled your bet.\nGood for you"
                server_data["joinees"][str(ctx.author.id)]["value"] += amount
            elif roll > 60:
                title = "Okay, I guess"
                description = "You just made back what you gambled.\nNo loss no gain"
            elif roll < 30:
                title = "Nice going"
                description = "You just lost double your bet.\nImpressive"
                server_data["joinees"][str(ctx.author.id)]["value"] -= amount*2
            else:
                title = "Lol"
                description = "You lost your bet.\nNice going lmao"
                server_data["joinees"][str(ctx.author.id)]["value"] -= amount
            
            if server_data["joinees"][str(ctx.author.id)]["value"] < 0:
                server_data["joinees"][str(ctx.author.id)]["value"] = 0


            await oap.give_output(
                embed_title=title,
                embed_description=description + f"\nNow you're worth {server_data['joinees'][str(ctx.author.id)]['value']}",
                log_text="Got their value",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

            if server_data["joinees"][str(ctx.author.id)]["value"] <= 0:
                del server_data["joinees"][str(ctx.author.id)]

                await oap.give_output(
                    embed_title="Nice going",
                    embed_description="Now you're dead",
                    log_text="Got killed",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

                # try:
                #     await ctx.author.kick()
                #     return ctx.author.send("You died!")
                # except:
                #     pass
            
            return



        return await oap.give_output(
            embed_title="You haven't been dragged into hell yet",
            embed_description=f"`>>join` the circus to have value",
            log_text="Tried to get their value",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )





















    
    @commands.command()
    async def steal(self, ctx, amount="", person:discord.Member=None):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if not server_data.get("joinees"):
            server_data["joinees"] = {}

        if str(ctx.author.id) in [key for key, value in server_data["joinees"].items()]:
            if amount == "":
                return await oap.give_output(
                    embed_title="You hafta give an amount to steal",
                    embed_description=f"Otherwise what would you ~~lose~~ gain?",
                    log_text="Tried to steal nothing",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            try:
                amount = int(amount)
            except:
                return await oap.give_output(
                    embed_title="You must give a number as how much you want to steal",
                    embed_description=f"I don't take material posessions, only meaningless measures of self-worth",
                    log_text="Tried to steal a material posession",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            if not person:
                return await oap.give_output(
                    embed_title="You hafta give a person to steal from",
                    embed_description=f"Just ping them, or use their id, or something",
                    log_text="Tried to steal from no one",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            if str(person.id) == str(ctx.author.id):
                return await oap.give_output(
                    embed_title="What are you trying to do??!?",
                    embed_description=f"You can't steal from yourself!",
                    log_text="Tried to steal from themself",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

            if str(person.id) in [key for key, value in server_data["joinees"].items()]:
                if amount > server_data["joinees"][str(person.id)]["value"]:
                    return await oap.give_output(
                        embed_title="You can't steal more than they have",
                        embed_description=f"I don't just create this from nowhere, you know",
                        log_text="Tried to steal more than they have",
                        cog=self.cog_name,
                        ctx=ctx,
                        data=server_data
                    )

                num = randint(0, 99)

                value = (amount) if amount < server_data["joinees"][str(ctx.author.id)]["value"] else server_data["joinees"][str(ctx.author.id)]["value"]
                value2 = (amount*2) if amount < server_data["joinees"][str(ctx.author.id)]["value"] else server_data["joinees"][str(ctx.author.id)]["value"]
                value4 = (amount*4) if amount < server_data["joinees"][str(ctx.author.id)]["value"] else server_data["joinees"][str(ctx.author.id)]["value"]

                if num == 99:
                    title = "God damn!"
                    description = "You managed to steal *quadruple* the amount!\nGo off, I guess"
                    server_data["joinees"][str(ctx.author.id)]["value"] += amount * 4
                    server_data["joinees"][str(person.id)]["value"] -= amount * 4
                elif num >= 90:
                    title = "Good job!"
                    description = "You snuck in and managed to get double what you were trying for!\nYou got some big pockets"
                    server_data["joinees"][str(ctx.author.id)]["value"] += amount * 2
                    server_data["joinees"][str(person.id)]["value"] -= amount * 2
                elif num > 75:
                    title = "Nice work"
                    description = f"You successfully robbed an innocent person of {amount}.\nHooray!"
                    server_data["joinees"][str(ctx.author.id)]["value"] += amount
                    server_data["joinees"][str(person.id)]["value"] -= amount
                elif num < 25:
                    title = "Epic"
                    description = "You snuck in and managed not only to get caught, but beat up too.\nYou lost double what you were trying to get"
                    server_data["joinees"][str(ctx.author.id)]["value"] -= value2
                    server_data["joinees"][str(person.id)]["value"] += value2
                elif num < 5:
                    title = "Dude."
                    description = "You snuck in, walked into every trap possible, and tripped directly into their arms.\nYou lost quadruple what you were trying to get"
                    server_data["joinees"][str(ctx.author.id)]["value"] -= value4
                    server_data["joinees"][str(person.id)]["value"] += value4
                else:
                    title = "Nice one"
                    description = "You snuck in and managed to get caught.\nYou lost what you were trying to get"
                    server_data["joinees"][str(ctx.author.id)]["value"] -= value
                    server_data["joinees"][str(person.id)]["value"] += value

                
                await oap.give_output(
                    embed_title=title,
                    embed_description=description + f"\nNow you're worth {server_data['joinees'][str(ctx.author.id)]['value']}\nNow they're worth {server_data['joinees'][str(person.id)]['value']}",
                    log_text="Stole from someone",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data
                )

                if server_data["joinees"][str(ctx.author.id)]["value"] <= 0:
                    del server_data["joinees"][str(ctx.author.id)]

                    await oap.give_output(
                        embed_title="Nice going",
                        embed_description="Now you're dead",
                        log_text="Got killed",
                        cog=self.cog_name,
                        ctx=ctx,
                        data=server_data
                    )

                    # try:
                    #     await ctx.author.kick()
                    #     return ctx.author.send("You died!")
                    # except:
                    #     pass

                if server_data["joinees"][str(person.id)]["value"] <= 0:
                    del server_data["joinees"][str(person.id)]

                    await oap.give_output(
                        embed_title="Congrats!",
                        embed_description="Now they're dead.\nYou killed someone today, I hope you're proud!",
                        log_text="Got killed",
                        cog=self.cog_name,
                        ctx=ctx,
                        data=server_data
                    )

                    # try:
                    #     await person.kick()
                    #     return person.send("You died!")
                    # except:
                    #     pass
                
                return

            return await oap.give_output(
                embed_title="They haven't been sent into the depths yet",
                embed_description=f"Get them to `>>join` before doing anything to them",
                log_text="Tried to steal from someone not joined",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        return await oap.give_output(
            embed_title="You haven't been dragged into hell yet",
            embed_description=f"`>>join` the circus to have value",
            log_text="Tried to steal and hasnt joined",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )

















    


    @commands.command()
    async def who(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if not server_data.get("joinees"):
            server_data["joinees"] = {}

        if str(ctx.author.id) in [key for key, value in server_data["joinees"].items()]:
            return await oap.give_output(
                embed_title="Hm?",
                embed_description=f"""\
                    Oh, you want me to tell you who else is in hell with you?

                    Alright, fine.

                    {oap.linebreak.join([f"<@{key}>" for key, person in server_data["joinees"].items()])}
                    """,
                log_text="Listed users",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        return await oap.give_output(
            embed_title="You haven't been dragged down",
            embed_description="You can't see who's in hell unless you're there with them",
            log_text="Tried to see who's in hell",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )


def setup(bot):
    oap.log(text="Loaded", cog="Stupid")
    stupid = Stupid(bot)
    bot.add_cog(stupid)
    reload(oap)