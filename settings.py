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
    # TODO: only server managers can change this    
    # ==================================================
    @commands.command(brief="Toggle whether or not to delete invocation messages", help="By default, Abacus doesn't delete invocation messages (the message with the command in it). If this is on, Abacus will delete those messages.")
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
# Cog Setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Settings", color="yellow")
    bot.add_cog(Settings(bot))
    reload(oap)
