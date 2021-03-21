import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from importlib import reload
import emoji as em
import discord
import re


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
    @commands.command(brief="Toggle whether or not to delete invocation messages", help="__**Required Permissions**__\n- Manage Server\n\nBy default, Abacus doesn't delete invocation messages (the message with the command in it). If this is on, Abacus will delete those messages.\n\n__**Examples**__\n`>>toggle_delete_invocation`")
    @commands.has_permissions(manage_guild=True)
    async def toggle_delete_invocation(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        changed_to = None

        # ==================================================
        # Get values and switch them accordingly
        # ==================================================
        if server_data.get("delete_invocation") == True:
            server_data["delete_invocation"] = False
            changed_to = "False"
        elif server_data.get("delete_invocation") in [False, None]:
            server_data["delete_invocation"] = True
            changed_to = "True"

        # ==================================================
        # Set data, send output, and log to console
        # ==================================================
        embed = oap.makeEmbed(title="Success!", description=f"Invocation deletion for the server \"{ctx.guild.name}\" has been set to {changed_to}", ctx=ctx)
        await ctx.send(embed=embed)
        oap.setJson(f"servers/{ctx.guild.id}", server_data)
        oap.log(text=f"Changed invocation deletion to {changed_to}", cog="Settings", color="yellow", ctx=ctx)

    
    # ==================================================
    # Poll settings command
    # ==================================================
    @commands.command(brief="Change default settings for the poll command", usage="[category] [setting]", help="__**Required Permissions**__\n- Manage Server\n\nChange the default settings for polls on this server.\n\n__**Examples**__\n`>>poll_settings emoji yes :thumbsup:`\n`>>poll_settings emoji no reset`\n`>>poll_settings emoji all reset`")
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

            # ==================================================
            # Set variables
            # ==================================================
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
            # Set data, send ouput, log to console
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
            # Set data, send output, log to console
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
    # User settings command
    # ==================================================
    @commands.command(brief="Change your user settings", usage="[category] [value]", help="Change your user-specific settings.\n\n__**Examples**__\n`>>user_settings color`\n`>>user_settings color 2083ff`\n`>>user_settings color reset`")
    async def user_settings(self, ctx, category="", *, input=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        user_data = oap.getJson(f"users/{ctx.author.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        categories = ["color"]
    
        # ==================================================
        # Arg checking
        # ==================================================
        if category == "":
            embed = oap.makeEmbed(title="Please Enter a Category!", description="Valid categories are:\n" + ("\n- ".join(categories)), ctx=ctx)
            return await ctx.send(embed=embed)

        if category not in categories:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid category\nValid categories are:\n- " + ("\n- ".join(categories)), ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # If they input the color category
        # ==================================================
        if category == "color":
            # ==================================================
            # Check if they input nothing
            # Give them information if they did
            # ==================================================
            if input == "":
                if user_data.get("color"):
                    embed = oap.makeEmbed(title="Here You Go!", description=f"Your color is {hex(user_data['color'])}", ctx=ctx)
                    return await ctx.send(embed=embed)
                else:
                    embed = oap.makeEmbed(title="Whoops!", description=f"You dont have a color yet\nSet one with >>user_settings color [hex codee]", ctx=ctx)
                    return await ctx.send(embed=embed)

            # ==================================================
            # Check if they input "reset"
            # If so, just delete their set color
            # Then send output and log to console
            # ==================================================
            if input == "reset":
                del user_data["color"]

                oap.setJson(f"users/{ctx.author.id}", user_data)
                embed = oap.makeEmbed(title="Success!", description=f"Your color has been reset", ctx=ctx)
                await ctx.send(embed=embed)
                return oap.log(text="Reset their user color", cog="Settings", color="yellow", ctx=ctx)

            # ==================================================
            # Get rid of any starting hashtag
            # And check if they gave a valid length color
            # ==================================================
            if input.startswith("#"):
                input = input[1:]
            if len(input) != 6:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid hex code for your color", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Try making the color an integer
            # If it doesnt work, say so
            # ==================================================
            try:
                color = int(f"0x{input}", 16)
            except:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid hex code for your color", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Set their data
            # Send output
            # Log to console
            # ==================================================
            user_data["color"] = color
            oap.setJson(f"users/{ctx.author.id}", user_data)
    
            embed = oap.makeEmbed(title="Success!", description=f"Your color has been set to 0x{input}", ctx=ctx)
            await ctx.send(embed=embed)
            oap.log(text="Changed their user color", cog="Settings", color="yellow", ctx=ctx)


    # ==================================================
    # Hall of fame and shame config
    # ==================================================

    @commands.command(brief="Change hall of fame and shame settings", usage="[fame, shame, or message] [setting] [value]", help="__**Required Permissions**__\n- Manage Server\n\nChange the settings for hall of fame and hall of shame.\n\n__**What?**__\n- The hall of fame and hall of shame are places where messages will get sent, if given a specific amount of reactions.\n- By default, if a message gets four ⬆️ reactions, it will be sent in a designated hall of fame channel (if there is one), and the opposite for ⬇️.\n\n__**Emoji**__\n- Change the emoji that users must react with.\n`>>hall_settings fame emoji :thumbsup:`\n`>>hall_settings shame emoji reset`\n\n__**Requirement**__\n- Change the amount of each reaction required for the message to be sent in a channel.\n`>>hall_settings fame requirement 12`\n`>>hall_settings shame requirement reset`\n\n__**Channel**__\n- Change which channel the bot should send messages in when they get enough reactions.\n`>>hall_settings fame channel #hall-of-fame`\n`>>hall_settings shame channel reset`\n\n__**Announcement Messages**__\n- Change what message the bot will send when a user gets enough reactions.\n`>>hall_settings fame message [user] is super cool!`\n`>>hall_settings fame removal_message [user] is no longer cool`\n`>>hall_settings shame message [user] is totally lame :/`\n`>>hall_settings shame removal_message reset`\n\n__**Message**__\n- Change the message that gets sent in the hall of fame or shame.\n`>>hall_settings message \"[[channel]] **[user]**: [message]\n([attachments])\"`\n`>>hall_settings message reset`")
    @commands.has_permissions(manage_guild=True)
    async def hall_settings(self, ctx, which="", setting="", *, input=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Argument checking
        # ==================================================
        if which == "":
            embed = oap.makeEmbed(title="Whoops!", description="Please enter the hall you want to change settings for (fame or shame)", ctx=ctx)
            return await ctx.send(embed=embed)
        
        if which not in ["fame", "shame", "message"]:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter either fame or shame as the hall you want to change\nYou can also enter 'message' to change how the message is formatted when someone gets put in a hall", ctx=ctx)
            return await ctx.send(embed=embed)

        default = {
            "fame": {
                "emoji": "⬆️",
                "requirement": 4,
                "channel": None,
                "message": "[user] was sent to the hall of fame!",
                "removal_message": "[user] was removed from the hall of fame!"
            },
            "shame": {
                "emoji": "⬇️",
                "requirement": 4,
                "channel": None,
                "message": "[user] was sent to the hall of shame!",
                "removal_message": "[user] was removed from the hall of shame!"
            },
            "message": "**[user]:** [message]\n\n[attachments]"
        }

        # ==================================================
        # Check if server data exists
        # If not, set to defaults
        # ==================================================
        if not server_data.get("halls"):
            server_data["halls"] = default

        # ==================================================
        # If they entered to change the message
        # Check if they entered a message
        # ==================================================
        if which == "message":
            if setting == "":
                embed = oap.makeEmbed(title="Whoops!", description="If you wish to change this, enter a message, surrouned by quotes\nYou can use discords formatting, and variables such as [user], [message], [attachments], or [channel]", ctx=ctx)
                embed.add_field(name="Current Message", value=server_data["halls"]["message"], inline=False)
                return await ctx.send(embed=embed)
            if not server_data.get("halls"):
                server_data["halls"] = default
            old_value = server_data.get("message")
            server_data["message"] = setting

            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Successfully changed the default message format\n\n*If this doesnt look correct, make sure you put the message in quotes*", ctx=ctx)
            embed.add_field(name="Old Value", value=str(old_value), inline=False)
            embed.add_field(name="New Value", value=str(input))
            await ctx.send(embed=embed)
            return oap.log(text="Changed the hall message format", cog="Settings", color="yellow", ctx=ctx)

        # ==================================================
        # If they didnt input a setting to change
        # Just give them current settings
        # ==================================================
        if setting == "":
            embed = oap.makeEmbed(title=f"Current Hall of {which.title()} Settings", description=f"*Any of these can be changed*", ctx=ctx)
            embed.add_field(name="Emoji", value=server_data.get("halls").get(which).get("emoji"))
            embed.add_field(name="Requirement", value=server_data.get("halls").get(which).get("requirement"))
            embed.add_field(name="Channel", value=server_data.get("halls").get(which).get("channel"))
            embed.add_field(name="Message", value=server_data.get("halls").get(which).get("message"))
            embed.add_field(name="Removal Message", value=server_data.get("halls").get(which).get("removal_message"))

            # ==================================================
            # Send output
            # Log to console
            # ==================================================
            await ctx.send(embed=embed)
            return oap.log(text=f"Got hall of {which} settings", cog="Settings", color="yellow", ctx=ctx)

        # ==================================================
        # If they *did* give a setting to change
        # Check if it's a valid setting
        # ==================================================
        if setting not in ["emoji", "requirement", "channel", "message", "removal_message"]:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid setting to change", ctx=ctx)
            embed.add_field(name="Valid Settings", value="- emoji\n- requirement\n- channel\n- message\n- removal_message", inline=False)
            return await ctx.send(embed=embed)

        # ==================================================
        # Check if the value they gave is valid
        # ==================================================
        if setting == "emoji":
            if input == "reset":
                input = "⬆️" if which == "fame" else "⬇️"
            elif input not in em.UNICODE_EMOJI and not re.match(r"(:([^\s:]+):(?!\d))|(<(:|(a:))([^\s<>]+):(\d{18})>)", input):
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid emoji", ctx=ctx)
                return await ctx.send(embed=embed)

        if setting == "requirement":
            if input == "reset":
                input = 4
            try:
                input = int(input)
                if input < 1:
                    embed = oap.makeEmbed(title="Whoops!", description="Please enter a positive, nonzero integer", ctx=ctx)
                    return await ctx.send(embed=embed)
            except:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid number", ctx=ctx)
                return await ctx.send(embed=embed)

        if setting == "channel":
            if input == "reset":
                input = "None"
            if not re.match(r"(<#(\d+)>)", input) and input != "None":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid channel", ctx=ctx)
                return await ctx.send(embed=embed)

        if setting == "message":
            if input == "reset":
                input = f"[user] was sent to the hall of {which}!"

        if setting == "removal_message":
            if input == "reset":
                input = f"[user] was removed from the hall of {which}!"

        old_value = server_data["halls"][which][setting]
        server_data["halls"][which][setting] = None if input == "None" else input
        
        # ==================================================
        # Save data
        # Send output
        # Log to console
        # ==================================================
        oap.setJson(f"servers/{ctx.guild.id}", server_data)
        embed = oap.makeEmbed(title="Success!", description=f"Successfully changed the hall of {which}'s {setting}", ctx=ctx)
        embed.add_field(name="Old Value", value=str(old_value), inline=False)
        embed.add_field(name="New Value", value=str(input))
        await ctx.send(embed=embed)
        oap.log(text="Changed a hall setting", cog="Settings", color="yellow", ctx=ctx)

    # ==================================================
    # Autoresponders settings
    # ==================================================
    @commands.command(brief="Change autoresponder settings", help="__**Required Permissions**__\n- Manage Server\n\nAdd, remove, and edit autoresponders for this server.\n\n__**Examples**__\n`>>autoresponders toggle`\n`>>autoresponders add word/anywhere/beginning/end bro bro!!`")
    async def autoresponders(self, ctx, which="", num="", trigger="", response=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # >>autoresponders add/remove/edit/list  trigger/number trigger/response trigger/response
    
        # ==================================================
        # Argument checking
        # ==================================================
        if which == "toggle":
            if not server_data.get("autoresponder"):
                server_data["autoresponder"] = False

            server_data["autoresponder"] = False if server_data["autoresponder"] else True

            oap.setJson(f"servers/{ctx.guild.id}", server_data)

            embed = oap.makeEmbed(title="Success!", description=f"Autoresponders have been toggled for this server")
            await ctx.send(embed=embed)
            return oap.log(text="Toggled autoresponders", cog="Settings", color="yellow", ctx=ctx)

        if which == "add":
            if not server_data.get("autoresponders"):
                server_data["autoresponders"] = []

            server_data["autoresponders"].append({
                "type": num,
                "trigger": trigger,
                "response": response
            })

            oap.setJson(f"servers/{ctx.guild.id}", server_data)

            embed = oap.makeEmbed(title="Success!", description=f"Autoresponder added\n\n**Trigger:** {trigger}\n**Response:** {response}")
            await ctx.send(embed=embed)
            return oap.log(text="Added an autoresponder", cog="Settings", color="yellow", ctx=ctx)
    
        # ==================================================
        # Send output
        # Log to console
        # ==================================================
        # embed = oap.makeEmbed(title="PLACEHOLDER", description="PLACEHOLDER", ctx=ctx)
        # await ctx.send(embed=embed)
        # oap.log(text="PLACEHOLDER", cog="PLACEHOLDER", color="PLACEHOLDER", ctx=ctx)


# ==================================================
# Cog Setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Settings", color="yellow")
    bot.add_cog(Settings(bot))
    reload(oap)
