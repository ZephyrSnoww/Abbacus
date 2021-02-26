import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from importlib import reload
import discord


class Settings(commands.Cog, description="Settings, per-server or per-user"):
    def __init__(self, bot):
        self.abacus = bot
        self.data = oap.getJson("data")

    # ==================================================
    # Unload Event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="Settings", color="yellow")


    # ==================================================
    # Toggle delete invocation command 
    # ==================================================
    @commands.command(brief="Toggle whether or not to delete invocation messages", help="By default, Abacus doesn't delete invocation messages (the message with the command in it). If this is on, Abacus will delete those messages.")
    @commands.has_permissions(manage_guild=True)
    async def toggle_delete_invocation(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        changed_to = None

        if server_data.get("delete_invocation") == True:
            server_data["delete_invocation"] = False
            changed_to = "False"
        elif server_data.get("delete_invocation") in [False, None]:
            server_data["delete_invocation"] = True
            changed_to = "True"

        embed = oap.makeEmbed(title="Success!", description=f"Invocation deletion for the server \"{ctx.guild.name}\" has been set to {changed_to}", ctx=ctx)
        await ctx.send(embed=embed)
        oap.setJson(f"servers/{ctx.guild.id}", server_data)
        oap.log(text=f"Changed invocation deletion to {changed_to}", cog="Settings", color="yellow", ctx=ctx)

    
    # ==================================================
    # Poll settings command
    # ==================================================
    @commands.command(brief="Change default settings for the poll command", usage="[category] [setting]", help="")
    @commands.has_permissions(manage_guild=True)
    async def poll_settings(self, ctx, category="", *, value=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Arg checking
        # ==================================================
        if category == "":
            embed = oap.makeEmbed(title="Please Enter a Category", description="Valid categories are:\n- emoji\n- timer\n- invocation", ctx=ctx)
            return await ctx.send(embed=embed)
        
        if category not in ["emoji", "timer", "invocation"]:
            embed = oap.makeEmbed(title="Whoops!", description="You entered an invalid category\nValid categories are:\n- emoji\n- timer\n- invocation", ctx=ctx)
            return await ctx.send(embed=embed)

        
        # ==================================================
        # If theyre changing emoji
        # ==================================================
        if category == "emoji":
            # ==================================================
            # Arg check the value argument
            # ==================================================
            if value == "" or value.split(" ")[0] not in ["yes", "no", "shrug", "all"]:
                embed = oap.makeEmbed(title="Please Enter a Valid Emoji Type to Change", description="Emoji you can set are \"yes\", \"no\", \"shrug\", or \"all\"", ctx=ctx)
                return await ctx.send(embed=embed)

            if len(value.split(" ")) == 1:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter an emoji to change to, or \"reset\"", ctx=ctx)
                return await ctx.send(embed=embed)

            value = value.split(" ")
            which_emoji = value[0]
            emoji = value[1]

            # ==================================================
            # Check if the emoji is from the server
            # ==================================================
            if emoji != "reset":
                try:
                    await ctx.message.add_reaction(emoji)
                    await ctx.message.remove_reaction(emoji, self.abacus.user)
                except:
                    embed = oap.makeEmbed(title="Whoops!", description="That emoji isn't from this server", ctx=ctx)
                    return await ctx.send(embed=embed)

            # ==================================================
            # Get server data (if it exists, otherwise a default dict)
            # ==================================================
            if server_data.get("poll"):
                data = server_data.get("poll")
            else:
                data = {
                    "yes": "",
                    "no": "",
                    "shrug": ""
                }
                
            # ==================================================
            # Change the single (or all) emoji
            # ==================================================
            if which_emoji != "all":
                if emoji == "reset":
                    data[which_emoji] = ""
                    out = f"The default {which_emoji} emoji has been reset"
                else:
                    data[which_emoji] = emoji
                    out = f"The default {which_emoji} emoji has been set to {emoji}"
            else:
                if emoji == "reset":
                    data = {
                        "yes": "",
                        "no": "",
                        "shrug": ""
                    }
                    out = f"All default emoji have been reset"
                else:
                    data = {
                        "yes": emoji,
                        "no": emoji,
                        "shrug": emoji
                    }
                    out = f"All default emoji have been set to {emoji}"

            # ==================================================
            # Set data and send ouput
            # ==================================================
            server_data["poll"] = data
            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=out, ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text=f"Changed {which_emoji} default poll emoji to {emoji}", cog="Settigns", color="yellow", ctx=ctx)

        # ==================================================
        # If theyre changing invocation
        # ==================================================
        elif category == "invocation":
            if server_data.get("poll"):
                data = server_data.get("poll")
            else: 
                data = {}

            # ==================================================
            # Get and switch delete_invocation value
            # ==================================================
            if isinstance(data.get("delete_invocation"), bool):
                if data["delete_invocation"] == True:
                    data["delete_invocation"] = False
                else:
                    data["delete_invocation"] = True
            else:
                data["delete_invocation"] = False

            # ==================================================
            # Set data and send output
            # ==================================================
            server_data["poll"] = data
            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"delete_invocation has been set to {data['delete_invocation']}")
            await ctx.send(embed=embed)
            return oap.log(text=f"Changed poll invocation deletion to {data['delete_invocation']}", cog="Settigns", color="yellow", ctx=ctx)

        # ==================================================
        # If theyre changing timer settings
        # ==================================================
        embed = oap.makeEmbed(title="Whoops!", description="Timer settings aren't available yet\nCheck back soon", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Tried to change timer settings", cog="Settigns", color="yellow", ctx=ctx)


# ==================================================
# Cog Setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Settings", color="yellow")
    bot.add_cog(Settings(bot))
    reload(oap)
