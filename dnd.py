import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from importlib import reload
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


    # Get info from a category ==================================================
    # @commands.command(brief="", usage="", help="")
    # async def category(self, ctx, category=""):
    #     server_data = oap.getJson(f"servers/{ctx.guild.id}")
    #     if server_data.get("delete_invocation") == True:
    #         await oap.tryDelete(ctx)
    
    #     request = r.get(url=self.url).json()
    #     categories = request.keys()

    #     if category == "" or (category not in categories):
    #         embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid category\n*(You can get valid categories with >>available_categories)*", ctx=ctx)
    #         return await ctx.send(embed=embed)
        
    #     request = r.get(url=f"{self.url}/{category}").json()
    #     results = request.get("results")

    #     if len("- " + "\n- ".join([result.get("index") for result in results])) > 500:
    #         whole_string = "- " + "\n- ".join([result.get("index") for result in results])
    #         strings = [whole_string[:500] + "..."]
    #         for i in range(10):
    #             _string = whole_string[500*(i+1):]
    #             if len(_string) > 500:
    #                 strings.append("..." + _string[:500] + "...")
    #                 pass
    #             else:
    #                 strings.append("..." + _string)
    #                 break
            
    #         embeds = []
    #         for string in strings:
    #             embeds.append(oap.makeEmbed(title=f"Data From the {category.title()} Category", description=string, ctx=ctx))
            
    #         paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True, auto_footer=True)
    #         paginator.add_reaction('⏮️', "first")
    #         paginator.add_reaction('⏪', "back")
    #         paginator.add_reaction('🔐', "lock")
    #         paginator.add_reaction('⏩', "next")
    #         paginator.add_reaction('⏭️', "last")
    #         await paginator.run(embeds)
    #     else:
    #         embed = oap.makeEmbed(title=f"Data From the {category.title()} Category", description=("- " + "\n- ".join([result.get("index") for result in results])), ctx=ctx)
    #         await ctx.send(embed=embed)

    #     oap.log(text=f"Got info from the {category} category", cog="DND", color="magenta", ctx=ctx)


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
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="DND", color="magenta")
    bot.add_cog(DND(bot))
    reload(oap)
