import ovalia_auxiliary_protocol as oap
from discord.ext import commands
from importlib import reload
import requests
import discord
import urllib
import shutil


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
    
        acnh_data = oap.getJson("./cogs/acnh_data")

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


    # ==================================================
    # 
    # ==================================================
    @commands.command(brief="", help="""\
        help
        """)
    async def mtg(self, ctx, category="", value="", order="released", which="first"):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        valid_categories = [
            "card"
        ]

        if category not in valid_categories:
            return await oap.give_error(
                text = f"Please give a valid category!",
                categories = valid_categories,
                category_title = "Categories",
                examples = [
                    ">>mtg card \"Island\""
                ],
                ctx = ctx
            )

        if value == "":
            return await oap.give_error(
                text = f"Please give a value to search!",
                examples = [
                    ">>mtg card \"Island\""
                ],
                ctx = ctx
            )

        valid_orders = [
            "name",
            "set",
            "released",
            "rarity",
            "color",
            "usd",
            "tix",
            "eur",
            "cmc",
            "power",
            "toughness",
            "edhrec",
            "artist"
        ]

        if order not in valid_orders:
            return await oap.give_error(
                text = f"Please give a valid order!",
                categories = valid_orders,
                category_title = "Orders",
                ctx = ctx
            )

        valid_which = [
            "first",
            "last"
        ]

        if which not in valid_which:
            return await oap.give_error(
                text = f"Please give a valid card to get!",
                categories = valid_which,
                category_title = "Cards",
                ctx = ctx
            )

        response = requests.get(f"https://api.scryfall.com/{category}s/search?q={urllib.parse.quote(value)}&order={order}&include_extras=true&include_variations=true")

        if which == "first":
            card = response.json()['data'][0]
        else:
            card = response.json()['data'][-1]

        embed = oap.makeEmbed(
            title = f"{card['name']}",
            description = f"{card['rarity']}",
            image = f"{card['image_uris']['normal']}",
            ctx = ctx
        )

        embed.add_field(
            name = "Price",
            value = f"{card['prices']['usd']}"
        )

        embed.add_field(
            name = "Foil Price",
            value = f"{card['prices']['usd_foil']}"
        )

        embed.add_field(
            name = "Set",
            value = f"{card['set_name']}",
            inline = False
        )

        embed.add_field(
            name = "Type",
            value = f"{card['type_line']}",
            inline = False
        )

        embed.add_field(
            name = "Effect",
            value = f"{card['oracle_text']}",
            inline = False
        )

        embed.add_field(
            name = "Total Cards Found",
            value = f"{response.json()['total_cards']}",
            inline = False
        )

        embed.add_field(
            name = "Cards Found",
            value = "\n".join([response.json()['data'][i]['name'] for i in range(response.json()['total_cards'] if response.json()['total_cards'] <= 10 else 10)]) + ("\n..." if response.json()['total_cards'] > 10 else ""),
            inline = False
        )

        embed.set_footer(text=f"https://api.scryfall.com/{category}s/search?q={urllib.parse.quote(value)}&order={order}")

        return await oap.give_output(
            embed = embed,
            log_text = f"Got mtg data",
            cog = self.cog_name,
            ctx = ctx,
            data = server_data
        )


    # ==================================================
    # 
    # ==================================================
    @commands.command(brief="", help="""\
        help
        """)
    async def wolfram(self, ctx, *, input=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if input == "":
            return await oap.give_error(
                text = f"Please give input for wolfram alpha!",
                examples = [
                    ">>wolfram 2x2",
                    ">>wolfram roll 1d20",
                    ">>wolfram what is the parity of sin(x)"
                ],
                ctx = ctx
            )

        response = requests.get(f"http://api.wolframalpha.com/v1/simple?appid=A4HU5T-9PRV4Q9L4T&i={urllib.parse.quote(input)}&timeout=30", stream=True)

        if response.status_code == 200:
            with open("./images/wolfram.png", "wb") as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
            
            file = discord.File("./images/wolfram.png")
            return await ctx.send(file=file)
        elif response.status_code == 501:
            embed = oap.makeEmbed(
                title = f"Whoops!",
                description = "Wolfram couldn't interpret that question!\nTry again with something else!",
                ctx = ctx
            )
        elif response.status_code == 400:
            embed = oap.makeEmbed(
                title = f"Whoops!",
                description = "You managed to not give any input!",
                ctx = ctx
            )

        return await oap.give_output(
            embed = embed,
            log_text = f"Asked wolfram alpha a question",
            cog = self.cog_name,
            ctx = ctx
        )



def setup(bot):
    oap.log(text="Loaded", cog="Games")
    bot.add_cog(Games(bot))
    reload(oap)