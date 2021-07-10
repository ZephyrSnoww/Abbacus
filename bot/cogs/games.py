import ovalia_auxiliary_protocol as oap
from discord.ext import commands
from importlib import reload
import discord


class Games(commands.Cog, description="A lotta commands for a lotta games"):
    def __init__(self, bot):
        self.abacus = bot
        self.cog_name = "Games"
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
    async def acnh(self, ctx, type="", *, name=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        acnh_data = oap.getJson("acnh_data")

        if type == "" or type not in ["villager", "insect", "fish"]:
            return await oap.give_error(
                text=f"Please give what you want, and a name!",
                examples=[
                    "`>>acnh villager clyde`",
                    "`>>acnh insect common butterfly`",
                    "`>>acnh fish dace`"
                ],
                ctx=ctx
            )
        elif name == "":
            return await oap.give_error(
                text=f"Please give a name!",
                examples=[
                    "`>>acnh villager clyde`",
                    "`>>acnh insect common butterfly`",
                    "`>>acnh fish dace`"
                ],
                ctx=ctx
            )

        if type == "insect":
            if name.lower() not in [insct["name"].lower() for insct in acnh_data["insects"]]:
                return await oap.give_error(
                    text=f"Please enter a valid insect name!",
                    examples=[
                        "`>>acnh insect common butterfly`"
                    ],
                    ctx=ctx
                )

            for insct in acnh_data["insects"]:
                if insct["name"].lower() == name.lower():
                    insect = insct
                    break

            return await oap.give_output(
                embed=oap.makeEmbed(
                    title=f"{insect['name'].title()}",
                    description=f"""
                        *id: {insect['id']}*

                        **Price:** {insect['price']}
                        
                        **Time Available:** {insect['times']['text']}

                        __**Months Available**__
                        **Northern Hemisphere:** {insect['months']['northern']['text']}
                        **Southern Hemisphere:** {insect['months']['southern']['text']}
                        """,
                    ctx=ctx,
                    thumbnail=f"https://villagerdb.com/images/items/medium/{('-'.join(insect['name'].split(' ')).lower())}.png"
                ),
                log_text=f"Got an ACNH insect",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        if type == "fish":
            if name.lower() not in [fsh["name"].lower() for fsh in acnh_data["fish"]]:
                return await oap.give_error(
                    text=f"Please enter a valid fish name!",
                    examples=[
                        "`>>acnh fish dace`"
                    ],
                    ctx=ctx
                )

            for fsh in acnh_data["fish"]:
                if fsh["name"].lower() == name.lower():
                    fish = fsh
                    break

            return await oap.give_output(
                embed=oap.makeEmbed(
                    title=f"{fish['name'].title()}",
                    description=f"""
                        *id: {fish['id']}*

                        **Location:** {fish['location']}
                        **Size:** {fish['shadow_size']}
                        **Price:** {fish['price']}

                        **Time Available:** {fish['times']['text']}

                        __**Months Available**__
                        **Northern Hemisphere:** {fish['months']['northern']['text']}
                        **Southern Hemisphere:** {fish['months']['southern']['text']}
                        """,
                    ctx=ctx,
                    thumbnail=f"https://villagerdb.com/images/items/medium/{fish['name'].lower()}.png"
                ),
                log_text=f"Got an ACNH fish",
                cog=self.cog_name,
                ctx=ctx
            )

        if type == "villager":
            if name.lower() not in [vlgr["name"].lower() for vlgr in acnh_data["villagers"]]:
                return await oap.give_error(
                    text=f"Please give a valid villager name!",
                    examples=[
                        "`>>acnh villager clyde`"
                    ],
                    ctx=ctx
                )

            for vlgr in acnh_data["villagers"]:
                if vlgr["name"].lower() == name.lower():
                    villager = vlgr
                    break
            
            return await oap.give_output(
                embed=oap.makeEmbed(
                    title=f"{villager['name'].title()}",
                    description=f"""
                        *{villager["personality"]} {villager["gender"].lower()} {villager["species"].lower()}*

                        **Birthday:** {villager["birthday"]["text"]}
                        **Zodiac:** {villager["zodiac"]}
                        """,
                    ctx=ctx,
                    thumbnail=f"https://villagerdb.com/images/villagers/medium/{villager['name'].lower()}.png"
                ),
                log_text=f"Got an ANCH villager",
                cog=self.cog_name,
                ctx=ctx
            )


def setup(bot):
    oap.log(text="Loaded", cog="Games")
    bot.add_cog(Games(bot))
    reload(oap)