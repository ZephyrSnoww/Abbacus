import ovalia_auxiliary_protocol as oap
from discord.ext import commands
from sys import argv
import traceback
import discord
import difflib


# ==================================================
# TODO: Poll timers (NAH)
# TODO: WEBSERVER <---------------------
# ==================================================


# ==================================================
# Initialization
# Clear the console
# Initialize the bot
# ==================================================
oap.clear()
abacus = commands.Bot(command_prefix=">>", owner_id=184474965859368960, case_insensetive=True)
data = oap.getJson("data")
cogs = data["cogs"]

# ==================================================
# Remove the base help command
# (We define a custom one in the general cog)
# ==================================================
abacus.remove_command("help")

# ==================================================
# Load all cogs
# ==================================================
for extension in cogs:
    abacus.load_extension(extension)
    oap.log(text=f"{extension.title()} loaded")

# ==================================================
# Check for if someone is the owner
# ==================================================
def is_owner(ctx):
    return ctx.author.id == abacus.owner_id


# ==================================================
# Basic Events
# ==================================================
@abacus.event
async def on_connect():
    oap.log(text="Connected")


# @abacus.event
# async def on_disconnect():
#     oap.log(text="Disconnected")


# ==================================================
# On ready (bot loads)
# Change the bots presence to "listening to >>help"
# ==================================================
@abacus.event
async def on_ready():
    oap.log(text="Abacus online")
    await abacus.change_presence(status=discord.Status.online, activity=discord.Activity(type=2, name=">>help"))
    oap.log(text="Presence changed")


# ==================================================
# On guild join / leave
# Log to console
# ==================================================
@abacus.event
async def on_guild_join(guild):
    oap.log(text=f"Joined \"{guild.name}\"")


@abacus.event
async def on_guild_remove(guild):
    oap.log(text=f"Left \"{guild.name}\"")


# ==================================================
# On a command error
# ==================================================
@abacus.event
async def on_command_error(ctx, error):
    # ==================================================
    # Basically ignore if any of the following:
    # - Message starts with >>reload
    # - The command isnt found
    # - User doesnt have permissions
    # - The command is disabled
    # ==================================================
    if ctx.message.content.startswith(">>reload"):
        return
    if isinstance(error, discord.ext.commands.CommandNotFound):
        embed = oap.makeEmbed(
            title=f"Whoops!",
            description=f"That command doesnt exist!",
            ctx=ctx
        )
        
        if len(difflib.get_close_matches(ctx.message.content.split(" ")[0].split(">>")[1], [command.name for command in abacus.commands])) > 0:
            embed.add_field(
                name=f"Did You Mean...",
                value=">>" + "\n>>".join(difflib.get_close_matches(ctx.message.content.split(" ")[0].split(">>")[1], [command.name for command in abacus.commands], cutoff=0.5)),
                inline=False
            )
        
        return await oap.give_output(
            embed=embed,
            log_text=f"Tried to do a command that doesn't exist",
            cog=None,
            ctx=ctx
        )
    if isinstance(error, discord.ext.commands.MissingPermissions):
        embed = oap.makeEmbed(title="Whoops!", description="You dont have the correct permissions to do that command", ctx=ctx)
        await ctx.send(embed=embed)
        return oap.log(text=f"Tried to do a command they dont have permission to do", ctx=ctx)
    if isinstance(error, discord.ext.commands.DisabledCommand):
        embed = oap.makeEmbed(title="Whoops!", description="That command is disabled", ctx=ctx)
        await ctx.send(embed=embed)
        return oap.log(text=f"Tried to do a disabled command", ctx=ctx)

    # ==================================================
    # Get the owner by id
    # ==================================================
    author = await abacus.fetch_user(184474965859368960)

    # ==================================================
    # Make a big ass embed with all the error info
    # ==================================================
    embed1 = oap.makeEmbed(title="Yikes", description="```" + "\n".join(traceback.format_tb(error.original.__traceback__)) + "```")
    embed1.add_field(name="Command", value=ctx.message.content.split(" ")[0], inline=True)
    embed1.add_field(name="Message", value=ctx.message.content, inline=True)
    embed1.add_field(name="Server", value=ctx.guild.name, inline=True)
    embed1.add_field(name="Author", value=ctx.author.name, inline=True)
    embed1.add_field(name="Error", value=f"`{error.original}`", inline=True)

    # ==================================================
    # Send the embed to the owner
    # Give the user an error message
    # Log
    # ==================================================
    await author.send(embed=embed1)
    embed2 = oap.makeEmbed(title="Uh Oh!", description=f"Whatever you did, I got the following error.\nIve told my author about this, hopefully it should be fixed soon!", ctx=ctx)
    embed2.add_field(name="Error", value=f"`{error.original}`")
    await ctx.send(embed=embed2)
    oap.log(text=f"Got an error from the {ctx.message.content.split(' ')[0]} command", ctx=ctx)


# ==================================================
# Reload command
# ==================================================
@abacus.command(name="reload", brief="Reload one or all of Abacus' cogs", help="This command is owner-only.\n\nReload all cogs, or reload a specific cog. This refreshes the file and applies any changes made.", hidden=True)
@commands.check(is_owner)
async def _reload(ctx, cog="all"):
    server_data = oap.getJson(f"servers/{ctx.guild.id}")
    if not server_data.get("delete_invocation") in [None, False]: await oap.tryDelete(ctx)
    
    # ==================================================
    # Get the datafile and load cogs
    # ==================================================
    data = oap.getJson("data")
    cogs = data["cogs"]
    log = []

    # ==================================================
    # If no specific cog is given
    # Go through every cog
    # Try to load it - if that fails, try to reload it
    # If *that* fails, throw an error
    # ==================================================
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
    
    # ==================================================
    # Otherwise (they gave a specific cog)
    # Load/reload the specific cog and send output
    # ==================================================
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

# ==================================================
# If >>reload gets an error
# ==================================================
@_reload.error
async def _reload_error(ctx, error):
    # ==================================================
    # If the user isnt the bot owner (failed the check)
    # Say so and log to console
    # ==================================================
    if isinstance(error, commands.CheckFailure):
        await oap.tryDelete(ctx)
        embed = oap.makeEmbed(title="Whoops!", description="Only the bot owner can reload cogs", ctx=ctx)
        await ctx.send(embed=embed)
        oap.log(text="Tried to reload cog(s) - Missing permissions", ctx=ctx)


# ==================================================
# Run the bot
# ==================================================
tokens = oap.getJson("../../../bot_tokens")
abacus.run(tokens["Abacus"])