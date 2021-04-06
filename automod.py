from datetime import datetime, timedelta
import ovalia_auxiliary_protocol as oap
from discord.ext import commands
from importlib import reload
import discord


class Moderation(commands.Cog, description="Automatic moderation and mod abilities"):
    def __init__(self, bot):
        self.abacus = bot
        self.cog_name = "Moderation"
        self.data = oap.getJson("data")

    # ==================================================
    # Unload Event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog=self.cog_name)


    # ==================================================
    # 
    # ==================================================
    @commands.command(brief="", help="""\
        help
        """)
    async def create_embed(self, ctx):
        global get_channel, get_title, get_description, get_time, get_author, get_color

        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Define a check for recieving messages
        # (Just check if theauthor is the original author)
        # ==================================================
        def check(message):
            return message.author.id == ctx.author.id

        # ==================================================
        # Define all the needed variables
        # ==================================================
        channel = None
        title = None
        description = None
        time = True
        author = None
        color = 0xffadb6

        channel_ask = f"""\
            Please send the channel you'd like the embed to be sent in!
            You can also send \"here\", and I'll send it in this channel!"""

        title_ask = f"""\
            Please send the title you'd like to give the embed!"""

        description_ask = f"""\
            Please send the description you'd like to give the embed!"""

        time_ask = f"""\
            Would you like to have the time at the bottom of the embed?
            (yes or no)"""

        color_ask = f"""\
            Would you like to set a custom color for the embed?
            (send a hex code, or say no)"""

        author_ask = f"""\
            Would you like to show an author at the top of the embed?
            (ping an author, or say no)"""


        async def get_channel(final=False, error=False):
            global channel

            if not error:
                await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=channel_ask,
                    ctx=ctx
                )
            response = await self.abacus.wait_for("message", check=check)

            if response.content.lower() == "here":
                channel = ctx.channel
                if final:
                    return await get_final()
                return await get_title()
            elif response.content.lower() == "cancel":
                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Embed creation cancelled.",
                    ctx=ctx
                )
            elif len(response.channel_mentions) == 0:
                await oap.give_error(
                    text=f"Please tag a channel, or say \"here\"!\nYou can also send \"cancel\", and I'll stop giving you prompts.",
                    ctx=ctx
                )
                return await get_channel(error=True)
            else:
                channel = response.channel_mentions[0]
                if final:
                    return await get_final()
                return await get_title()

        
        async def get_title(final=False):
            global title

            await oap.give_output(
                embed_title=f"Alright!",
                embed_description=title_ask,
                ctx=ctx
            )
            response = await self.abacus.wait_for("message", check=check)

            if response.content.lower() == "cancel":
                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Embed creation cancelled.",
                    ctx=ctx
                )
            else:
                title = response.content
                if final:
                    return await get_final()
                return await get_description()


        async def get_description(final=False):
            global description

            await oap.give_output(
                embed_title=f"Alright!",
                embed_description=description_ask,
                ctx=ctx
            )
            response = await self.abacus.wait_for("message", check=check)

            if response.content.lower() == "cancel":
                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Embed creation cancelled.",
                    ctx=ctx
                )
            else:
                description = response.content
                if final:
                    return await get_final()
                return await get_time()

        
        async def get_time(final=False, error=False):
            global time

            if not error:
                await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=time_ask,
                    ctx=ctx
                )
            response = await self.abacus.wait_for("message", check=check)

            if response.content.lower() == "cancel":
                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Embed creation cancelled.",
                    ctx=ctx
                )
            elif response.content.lower() not in ["yes", "no"]:
                await oap.give_error(
                    text=f"Please send either \"yes\" or \"no\"!\nYou can also send \"cancel\", and I'll stop giving you prompts.",
                    ctx=ctx
                )
                return await get_time(error=True)
            else:
                time = True if response.content.lower() == "yes" else False
                if final:
                    return await get_final()
                return await get_color()


        async def get_color(final=False, error=False):
            global color

            if not error:
                await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=color_ask,
                    ctx=ctx
                )
            response = await self.abacus.wait_for("message", check=check)

            if response.content.lower() == "cancel":
                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Embed creation cancelled.",
                    ctx=ctx
                )
            elif response.content.lower() == "no":
                if final:
                    return await get_final()
                return await get_author()
            else:
                color_response = response.content.lower()
                if color_response.startswith("#"):
                    color_response = color_response[1:]

                try:
                    oap.hexToRGB(color_response)
                    color = int(f"0x{color_response}", 0)
                except:
                    await oap.give_error(
                        text=f"Please enter a valid hex code, or \"no\"!\nYou can also send \"cancel\", and I'll stop giving you prompts.",
                        ctx=ctx
                    )
                    return await get_color(error=True)

                color = int(f"0x{color_response}", 0)

                if final:
                    return await get_final()
                return await get_author()


        async def get_author(final=False, error=False):
            global author

            if not error:
                await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=author_ask,
                    ctx=ctx
                )
            response = await self.abacus.wait_for("message", check=check)

            if response.content.lower() == "cancel":
                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Embed creation cancelled.",
                    ctx=ctx
                )
            elif response.content.lower() == "no":
                author = None
                return await get_final()
            elif len(response.mentions) == 0:
                await oap.give_error(
                    text=f"Please ping a user, or say \"no\"!\nYou can also send \"cancel\", and I'll stop giving you prompts.",
                    ctx=ctx
                )
                return await get_author(error=True)
            else:
                author = response.mentions[0]
                return await get_final()


        async def get_final(error=False):
            global channel, title, description, time, author, color

            if not error:
                await oap.give_output(
                    embed=oap.makeEmbed(
                        title=title,
                        description=description,
                        timestamp=None if not time else (datetime.now()+timedelta(hours=6)),
                        author=author,
                        color=color
                    ),
                    ctx=ctx
                )
                
                await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"""
                        Does this look correct?
                        If it does, say \"yes\"!
                        If it doesn't, send what youd like to change.
                        If you want to cancel creation, say \"cancel\".""",
                    ctx=ctx
                )
            response = await self.abacus.wait_for("message", check=check)

            if response.content.lower() == "cancel":
                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Embed creation cancelled.",
                    ctx=ctx
                )
            elif response.content.lower() == "yes":
                await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"The embed has been sent!",
                    ctx=ctx
                )
                await channel.send(
                    embed=oap.makeEmbed(
                        title=title,
                        description=description,
                        timestamp=None if not time else (datetime.now()+timedelta(hours=6)),
                        author=author,
                        color=color
                    )
                )
                return oap.log(text="Created an embed", ctx=ctx, cog=self.cog_name)
            elif response.content.lower() not in ["channel", "title", "description", "author", "time", "color"]:
                await oap.give_error(
                    text=f"Please enter either \"yes\", \"cancel\", or an item to change!",
                    categories=[
                        "channel",
                        "title",
                        "description",
                        "author",
                        "time",
                        "color"
                    ],
                    category_title="Items",
                    ctx=ctx
                )
                return await get_final(error=True)
            else:
                function = globals()[f"get_{response.content.lower()}"]
                return await function(final=True)
            

        await get_channel()


def setup(bot):
    oap.log(text="Loaded", cog="Moderation")
    bot.add_cog(Moderation(bot))
    reload(oap)