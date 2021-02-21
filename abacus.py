from discord.ext import commands
from pretty_help import PrettyHelp, Navigation
import ovalia_auxiliary_protocol as oap
from sys import argv
import discord


# ==================================================
# Initialization
# ==================================================
oap.clear()
nav = Navigation()
abacus = commands.Bot(command_prefix=">>", owner_id=184474965859368960, help_command=PrettyHelp())
data = oap.getJson("data")
cogs = data["cogs"]

for extension in cogs:
    abacus.load_extension(extension)
    oap.log(text=f"{extension.title()} loaded")

def is_owner(ctx):
    return ctx.author.id == abacus.owner_id


# ==================================================
# Basic Events
# ==================================================
@abacus.event
async def on_connect():
    oap.log(text="Connected")


@abacus.event
async def on_disconnect():
    oap.log(text="Disconnected")


@abacus.event
async def on_ready():
    oap.log(text="Abacus online")
    await abacus.change_presence(status=discord.Status.online, activity=discord.Activity(type=2, name=">>help"))
    oap.log(text="Presence changed")


@abacus.event
async def on_command_error(ctx, error):
    author = await abacus.fetch_user(184474965859368960)
    embed1 = oap.makeEmbed(title="Yikes", description=f"Someone managed to get an error")
    embed1.add_field(name="Command", value=ctx.message.content.split(" ")[0], inline=True)
    embed1.add_field(name="Message", value=ctx.message.content, inline=True)
    embed1.add_field(name="Server", value=ctx.guild.name, inline=True)
    embed1.add_field(name="Author", value=ctx.author.name, inline=True)
    embed1.add_field(name="Error", value=f"`{error.original}`", inline=True)
    await author.send(embed=embed1)
    embed2 = oap.makeEmbed(title="Uh Oh!", description=f"Whatever you did, I got the following error.\nIve told my author about this, hopefully it should be fixed soon", ctx=ctx)
    embed2.add_field(name="Error", value=f"`{error.original}`")
    await ctx.send(embed=embed2)
    oap.log(text=f"Got an error from the {ctx.message.content.split(' ')[0]} command", ctx=ctx)


# ==================================================
# Basic commands
# ==================================================
@abacus.command(name="reload", brief="Reload one or all of Abacus' cogs", help="This command is owner-only.\n\nReload all cogs, or reload a specific cog. This refreshes the file and applies any changes made.", hidden=True)
@commands.check(is_owner)
async def _reload(ctx, cog="all"):
    server_data = oap.getJson(f"servers/{ctx.guild.id}")
    if not server_data.get("delete_invocation") in [None, False]: await oap.tryDelete(ctx)
    
    data = oap.getJson("data")
    cogs = data["cogs"]
    log = []
    if cog == "all":
        for extension in cogs:
            try:
                abacus.load_extension(extension)
                log.append(f"- **{extension.title()}** loaded successfully")
            except commands.ExtensionAlreadyLoaded:
                abacus.reload_extension(extension)
                log.append(f"- **{extension.title()}** reloaded successfully")
            except commands.ExtensionNotFound:
                embed = oap.makeEmbed(title="Whoops!", description=f"I couldn't find a cog with the name \"{extension}\"!", ctx=ctx)
                return await ctx.send(embed=embed)
        embed = oap.makeEmbed(title="Success!", description="\n".join(log), ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Reloaded all cogs", ctx=ctx)
    else:
        _type = "loaded"
        try:
            abacus.load_extension(cog)
        except commands.ExtensionAlreadyLoaded:
            abacus.reload_extension(cog)
            _type="reloaded"
        except commands.ExtensionNotFound:
            embed = oap.makeEmbed(title="Whoops!", description=f"I couldn't find a cog with the name \"{cog}\"!", ctx=ctx)
            return await ctx.send(embed=embed)
        embed = oap.makeEmbed(title="Success!", description=f"**{cog.title()}** {_type} successfully", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text=f"Reloaded {cog}", ctx=ctx)

@_reload.error
async def _reload_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await oap.tryDelete(ctx)
        embed = oap.makeEmbed(title="Whoops!", description="Only the bot owner can reload cogs", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Tried to reload cog(s) - Missing permissions", ctx=ctx)


# ==================================================
# Run the bot
# ==================================================
abacus.run(argv[1])
