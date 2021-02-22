import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from importlib import reload
from random import randint
import requests as r
import DiscordUtils
import discord
import json
import re


class DND(commands.Cog, description="Stat generation, information on items, spells, and the like, and more, for Dungeons and Dragons 5th edition"):
    def __init__(self, bot):
        self.abacus = bot
        self.data = oap.getJson("data")
        self.url = "https://www.dnd5eapi.co/api"

    # ==================================================
    # Unload event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="DND", color="magenta")


    # ==================================================
    # General "get"/"lookup" command
    # ==================================================
    @commands.command(brief="", usage="", help="", aliases=["get"])
    async def lookup(self, ctx, category="categories", item="", *, other=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # Get the 5e api website and all available categories
        # ==================================================
        request = r.get(url=self.url).json()
        categories = request.keys()


        # ==================================================
        # Argument error checking
        # ==================================================
        if category == "categories":
            embed = oap.makeEmbed(title="Available Categories", description=("- " + "\n- ".join(categories)), ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Got available categories", cog="DND", color="magenta", ctx=ctx)
        
        if (category not in categories):
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid category\n*(You can get valid categories with >>lookup categories)*", ctx=ctx)
            return await ctx.send(embed=embed)


        # ==================================================
        # If they want a whole category
        # (No specific item)
        # ==================================================
        if item == "":
            request = r.get(url=f"{self.url}/{category}").json()
            results = request.get("results")

            # ==================================================
            # Get all category info
            # Spit it into strings small enough for discord (if necesarry)
            # Paginate it (if necesarry)
            # ==================================================
            if len("- " + "\n- ".join([result.get("index") for result in results])) > 500:
                whole_string = "- " + "\n- ".join([result.get("index") for result in results])
                strings = [whole_string[:500] + "..."]
                for i in range(10):
                    _string = whole_string[500*(i+1):]
                    if len(_string) > 500:
                        strings.append("..." + _string[:500] + "...")
                        pass
                    else:
                        strings.append("..." + _string)
                        break
                
                embeds = []
                for string in strings:
                    embeds.append(oap.makeEmbed(title=f"Data From the {category.title()} Category", description=string, ctx=ctx))
                
                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True, auto_footer=True)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⏪', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('⏩', "next")
                paginator.add_reaction('⏭️', "last")
                await paginator.run(embeds)
            else:
                embed = oap.makeEmbed(title=f"Data from the {category.title()} Category", description=("- " + "\n- ".join([result.get("index") for result in results])), ctx=ctx)
                await ctx.send(embed=embed)

            return oap.log(text=f"Got info from the {category} category", cog="DND", color="magenta", ctx=ctx)
    

        # ==================================================
        # Otherwise (they want a specific item)
        # ==================================================
        request = r.get(url=f"{self.url}/{category}").json()
        items = request.get("results")

        # ==================================================
        # Check if the item exists
        # ==================================================
        if item not in [item.get("index") for item in items]:
            embed = oap.makeEmbed(title="Whoops!", description="I couldnt find that item in that category", ctx=ctx)
            return await ctx.send(embed=embed)
        
        # ==================================================
        # Get the index of the item
        # Using the index, get the url of the item
        # ==================================================
        for number in range(len(items)): 
            if items[number].get("index") == item: 
                item_index = number
        request = r.get(url=f"https://www.dnd5eapi.co/{items[item_index].get('url')}").json()

        # ==================================================
        # If they specified something other than just the item
        # Iterate through what they requested
        # If something they requested is an array
        # Simplify it (or iterate through that until we find it)
        # ==================================================
        if other != "":
            for thing in other.split(" "):
                if isinstance(request, list):
                    for _item in request:
                        if _item.get(thing):
                            request = _item.get(thing)
                            break
                else:
                    request = request.get(thing)

        # ==================================================
        # If we never found their specific request, tell them
        # ==================================================
        if request == None:
            embed = oap.makeEmbed(title="Whoops!", description="I couldnt find that, try something else maybe?", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Formatting the request to JSON, if its an array
        # ==================================================
        if isinstance(request, list):
            request = json.loads("{\"" + other.split(" ")[-1] + "\": " + json.dumps(request) + "}")

        
        # ==================================================
        # If they *didnt* request something more specific than an item
        # ==================================================
        if other == "":
            formatted_category = re.sub(r'-', ' ', category).title()

            # ==================================================
            # Format the embed specifically for the information they requested
            # Yeah, this takes up a lot of space
            # ==================================================
            if category in ["conditions", "damage-types", "skills", "alignments"]:
                embed = oap.makeEmbed(title=f"Info on the {request.get('name')} {formatted_category[:-1] if formatted_category.endswith('s') else formatted_category}", description=("\n".join(request.get("desc")) if isinstance(request.get("desc"), list) else request.get("desc")), ctx=ctx)
            
            elif category == "ability-scores":
                embed = oap.makeEmbed(title=f"Info on the {request.get('full_name')} {formatted_category[:-1] if formatted_category.endswith('s') else formatted_category}", description="\n".join(request.get("desc")), ctx=ctx)
                embed.add_field(name="Skills", value="- " + "\n- ".join([f"{skill.get('name')} ({skill.get('url')[5:]})" for skill in request.get("skills")]), inline=True)
            
            elif category == "equipment-categories":
                whole_string = "- " + "\n- ".join([result.get("index") for result in request.get("equipment")])
                if len(whole_string) > 500:
                    strings = [whole_string[:500] + "..."]
                    for i in range(10):
                        _string = whole_string[500*(i+1):]
                        if len(_string) > 500:
                            strings.append("..." + _string[:500] + "...")
                            pass
                        else:
                            strings.append("..." + _string)
                            break

                    embeds = []
                    for string in strings:
                        embeds.append(oap.makeEmbed(title=f"Info on the {request.get('index')} Equipment Category", description=string, ctx=ctx))

                    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True, auto_footer=True)
                    paginator.add_reaction('⏮️', "first")
                    paginator.add_reaction('⏪', "back")
                    paginator.add_reaction('🔐', "lock")
                    paginator.add_reaction('⏩', "next")
                    paginator.add_reaction('⏭️', "last")
                    await paginator.run(embeds)
                else:
                    embed = oap.makeEmbed(title=f"Info on the {request.get('name')} Equipment Category", description=whole_string, ctx=ctx)
            
            elif category == "equipment":
                equipment_category = request.get("equipment_category").get("name")
                embed = oap.makeEmbed(title=f"Info on the {request.get('name')} {formatted_category[:-1] if formatted_category.endswith('s') else formatted_category}", description="*(" + ", ".join([(request.get(key) if isinstance(request.get(key), str) else request.get(key).get("name")) for key, value in request.items() if key.endswith("_category")]) + ")*", ctx=ctx)
                embed.add_field(name="Cost", value=f"{request.get('cost').get('quantity')} {request.get('cost').get('unit')}", inline=True)
                if equipment_category == "Adventuring Gear":
                    embed.add_field(name="Weight", value=f"{request.get('weight')}", inline=True)
                if equipment_category == "Mounts and Vehicles":
                    vehicle_category = request.get("vehicle_category")
                    if vehicle_category == "Mounts and Other Animals":
                        embed.add_field(name="Speed", value=f"{request.get('speed').get('quantity')} {request.get('speed').get('unit')}")
                        embed.add_field(name="Capacity", value=f"{request.get('capacity')}")
                    
                    # FUCKING ADD SHIT HERE
                    # YEAH
                    # YEAH
                    # YEAH
                    # YEAH
                    # YEAH
                    # YEAH
            
            # ==================================================
            # Fallback (if i havent written formatting for the category they chose)
            # Just do general formatting
            # ==================================================
            else:
                embed = oap.makeEmbed(title=f"HERE HAVE A BUNCH OF SHITTY {'JSON' if (isinstance(request, dict)) else 'not json'} DATA LOL!!!!!!!!!!!!!", description="```json\n" + ((json.dumps(request, indent=2) if (isinstance(request, dict)) else request) if len(json.dumps(request, indent=2) if (isinstance(request, dict)) else request) < 2000 else (json.dumps(request, indent=2) if (isinstance(request, dict)) else request)[:2000]) + "```", ctx=ctx)
        
        # ==================================================
        # Otherwise (requested something more specific than just an item)
        # Just do general formatting
        # ==================================================
        else:
            embed = oap.makeEmbed(title=f"HERE HAVE A BUNCH OF SHITTY {'JSON' if (isinstance(request, dict)) else 'not json'} DATA LOL!!!!!!!!!!!!!", description="```json\n" + ((json.dumps(request, indent=2) if (isinstance(request, dict)) else request) if len(json.dumps(request, indent=2) if (isinstance(request, dict)) else request) < 2000 else (json.dumps(request, indent=2) if (isinstance(request, dict)) else request)[:2000]) + "```", ctx=ctx)

        await ctx.send(embed=embed)
        oap.log(text=f"Got info on the {item} item from the {category} category", cog="DND", color="magenta", ctx=ctx)


    # ==================================================
    # Rolling stats
    # ==================================================
    @commands.command(brief="", usage="", help="")
    async def rollstats(self, ctx, *, _in=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Argument checking
        # Make the output dict
        # ==================================================
        ordered = False if _in == "" else True
        random = False
        if _in == "random":
            ordered = False
            random = True
        if ordered:
            for stat in _in.split(" "):
                if stat not in ["str", "dex", "con", "int", "wis", "cha"]:
                    embed = oap.makeEmbed(title="Whoops!", description=f"The stat \"{stat}\" is not a valid stat\nValid stats are str, dex, con, int, wis, or cha", ctx=ctx)
                    return await ctx.send(embed=embed)
        
        stats = {
            "str": 0,
            "dex": 0,
            "con": 0,
            "int": 0,
            "wis": 0,
            "cha": 0
        }

        # ==================================================
        # Rolling the numbers
        # (4d6, drop the lowest, six times)
        # ==================================================
        rolls = []
        for i in range(6):
            _rolls = [randint(1, 6) for i in range(4)]
            _rolls.remove(min(_rolls))
            rolls.append(sum(_rolls))

        # ==================================================
        # If they wanted an ordered list
        # Assign rolls to the stats highest to lowest
        # If they didnt specify every stat
        # Randomly choose the ones they didnt specify
        # ==================================================
        if ordered:
            for stat in _in.split(" "):
                stats[stat] = max(rolls)
                rolls.remove(max(rolls))
            if len(rolls) > 0:
                for stat in ["con", "dex", "str", "wis", "int", "cha"]:
                    if stats[stat] == 0:
                        stats[stat] = max(rolls)
                        rolls.remove(max(rolls))

        # ==================================================
        # If they want random stats
        # Randomly assign the stats
        # ==================================================
        elif random:
            for i in stats:
                index = randint(0, len(rolls)-1)
                stats[i] = rolls[index]
                del rolls[index]

        # ==================================================
        # If they dont want an ordered list or random stats
        # Just give them the six numbers
        # ==================================================

        embed = oap.makeEmbed(title="Rolled stats!", description=(", ".join([str(roll) for roll in rolls])) if (not ordered and not random) else ("\n".join([f"{key.title()}: {value}" for key, value in stats.items()])), ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Rolled stats", cog="DND", color="magenta", ctx=ctx)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="DND", color="magenta")
    bot.add_cog(DND(bot))
    reload(oap)
