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
            embed = oap.makeEmbed(title="Please Enter a Category!", description="Valid categories are:\n- emoji\n- timer\n- invocation", ctx=ctx)
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
                    embed = oap.makeEmbed(title="Whoops!", description=f"You dont have a color yet\nSet one with >>user_settings color [hex code]", ctx=ctx)
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
    @commands.command(brief="Change autoresponder settings", help="__**Required Permissions**__\n- Manage Server\n\nAdd, remove, and edit autoresponders for this server.\n\n__**Types**__\n- Autoresponders can have a type of \"word\", \"anywhere\", \"beginning\", or \"end\".\n- \"Word\" means it will only respond if the trigger is a word by itself (not contained within another word)\n- \"Anywhere\" will respond if the trigger is anywhere in the message.\n- \"Beginning\" and \"end\" will only respond if the trigger is at the beginning or end of the message.\n\n__**Examples**__\n`>>autoresponders toggle`\n`>>autoresponders list`\n`>>autoresponders add word bro bro!!`\n`>>autoresponders remove 1`\n`>>autoresponders edit 1 trigger dude`")
    @commands.has_permissions(manage_guild=True)
    async def autoresponders(self, ctx, which="", num="", trigger="", response=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # If they toggle autoresponders
        # Get data
        # If it doesnt exist, use defaults
        # ==================================================
        if which == "toggle":
            if not server_data.get("autoresponder"):
                server_data["autoresponder"] = False

            # ==================================================
            # Flip the value
            # ==================================================
            server_data["autoresponder"] = False if server_data["autoresponder"] else True

            # ==================================================
            # Write the data
            # Send output
            # Log to console
            # ==================================================
            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Autoresponders have been toggled {'on' if server_data['autoresponder'] else 'off'} for this server", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Toggled autoresponders", cog="Settings", color="yellow", ctx=ctx)

        # ==================================================
        # If they're adding an autoresponder
        # Make an empty dict if the data doesnt exist yet
        # ==================================================
        if which == "add":
            if not server_data.get("autoresponders"):
                server_data["autoresponders"] = []

            # ==================================================
            # Check if they entered a valid type
            # ==================================================
            if num not in ["word", "anywhere", "beginning", "end"]:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid autoresponder type\nValid types are word, anywhere, beginning, or end")
                return await ctx.send(embed=embed)

            # ==================================================
            # Add the autoresponder to the servers autoresponders
            # ==================================================
            server_data["autoresponders"].append({
                "type": num,
                "trigger": trigger,
                "response": response
            })

            # ==================================================
            # Write the data
            # Send output
            # Log to console
            # ==================================================
            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Autoresponder added\n\n**Trigger:** {trigger}\n**Response:** {response}\n\n*If these dont look how you wanted them to, make sure you surrounded the trigger and response in quotation marks!*", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Added an autoresponder", cog="Settings", color="yellow", ctx=ctx)

        # ==================================================
        # If they're removing an autoresponder
        # Send an error if the server doesnt have any
        # ==================================================
        if which == "remove":
            if not server_data.get("autoresponders") or len(server_data.get("autoresponders")) == 0:
                embed = oap.makeEmbed(title="Whoops!", description="This server doesn't have any autoresponders\nTry adding some with `>>autorespondsers add`", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Try to convert input to an int
            # If it fails, send em an error
            # ==================================================
            try:
                num = int(num)
            except:
                embed = oap.makeEmbed(title="Whoops!", description="That wasn't a valid autoresponder ID\nValid IDs are numbers\nGet all autoresponders with `>>autoresponders list`", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Check if the server actually has as many autoresponders as specified
            # ==================================================
            if len(server_data["autoresponders"]) < num:
                embed = oap.makeEmbed(title="Whoops!", description="That wasn't a valid autoresponder ID\nGet all autoresponders with `>>autoresponders list`", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Delete the given autoresponder
            # ==================================================
            deleted_auto = server_data["autoresponders"][num-1]
            del server_data["autoresponders"][num-1]

            # ==================================================
            # Save data
            # Send output
            # Log to console
            # ==================================================
            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Autoresponder removed\n\n**Trigger:** {deleted_auto['trigger']}\n**Response:** {deleted_auto['response']}", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Removed an autoresponder", cog="Settings", color="yellow", ctx=ctx)

        # ==================================================
        # If they're listing autoresponders
        # Send error if the server doesnt have any
        # ==================================================
        if which == "list":
            if not server_data.get("autoresponders") or len(server_data.get("autoresponders")) == 0:
                embed = oap.makeEmbed(title="Whoops!", description="This server doesn't have any autoresponders\nTry adding some with `>>autorespondsers add`", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Add each autoresponder's number and trigger to a string
            # ==================================================
            embed_description = "```"
            for i in range(len(server_data["autoresponders"])):
                autoresponder = server_data["autoresponders"][i]
                embed_description += (f"{i+1} - {autoresponder['trigger']} ({autoresponder['type']})\n")
            embed_description += "```"

            # ==================================================
            # Send embed with said string as description
            # Log to console
            # ==================================================
            embed = oap.makeEmbed(title=f"All Autoresponders for {ctx.guild.name}", description=embed_description, ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Got all autoresponders", cog="Settings", color="yellow", ctx=ctx)


    # ==================================================
    # Colored roles
    # ==================================================
    @commands.command(brief="Manage colored roles", help="*For this to work, I have to have a role above every other role in the server. This is a discord limitation, unfortunately*\n\n__**Required Permissions**__\n**Toggle**: Manage Server\n**Change Required Role**: Manage Server\n**Create/Edit/Delete**: Variable\n\nToggle, create, edit, and delete custom colored roles. This lets people give themselves custom colors without giving them new permissions and without any hassle.\n\n__**Toggle**__\nToggle colored roles off or on for this server. By default, anyone can create, edit, and delete colored roles - but only ones theyve created.\n`>>colored_roles toggle`\n\n__**Permissions**__\nAnyone with the Manage Server permission can set who can use this command. This allows you to set a role, and any user that doesn't have that role won't be able to use this command.\n`>>colored_roles role @Colorful`\n`>>colored_roles role reset`\n\n__**Create**__\nCreate a role with a specific name and hex color. I'll automatically give you the role, and place it above your current role. You cannot name a role something that already exists.\n`>>colored_role create Blue 4060ff`\n`>>colored_role create Green 22ff67`\n\n__**Edit**__\nEdit a pre-existing role that you've created. If you have the Manage Server permission, you can edit any created role.\n`>>colored_role edit Blue name Red`\n`>>colored_role edit Red color e05020`\n\n__**Delete**__\nRemove a role that you've created. If you have the Manage Server permission, you can remove any created role.\n`>>colored_role remove Red`", aliases=["colored_role"])
    async def colored_roles(self, ctx, _one="", _two="", _three="", _four=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Argument checking
        # ==================================================
        if _one not in ["toggle", "create", "edit", "delete", "role"]:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter either toggle, create, edit, delete, or role", ctx=ctx)
            return await ctx.send(embed=embed)

        default = {
            "enabled": False,
            "required_role": None,
            "roles": [
                # {
                #     "name": "Blue",
                #     "id": 12937819284752313,
                #     "creator": 98743218758769176
                # }
            ]
        }

        if not server_data.get("colored_roles"):
            server_data["colored_roles"] = default

        # ==================================================
        # If they want to toggle colored roles
        # ==================================================
        if _one == "toggle":
            # ==================================================
            # Check if the user has the manage server permission
            # ==================================================
            if not ctx.author.guild_permissions.manage_guild:
                embed = oap.makeEmbed(title="Whoops!", description="You don't have the required permissions to toggle colored roles\nOnly users with the Manage Server permission can do this", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Change the value in server_data
            # Write the data to the servers file
            # Send output
            # Log to console
            # ==================================================
            server_data["colored_roles"]["enabled"] = False if server_data["colored_roles"]["enabled"] == True else True
            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Colored roles have been {'enabled' if server_data['colored_roles']['enabled'] else 'disabled'} for this server", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text=f"Toggled role colors to {server_data['colored_roles']['enabled']}", cog="Settings", color="yellow", ctx=ctx)

        # ==================================================
        # If the server has colored roles disabled
        # Send an error
        # ==================================================
        if not server_data["colored_roles"]["enabled"]:
            embed = oap.makeEmbed(title="Whoops!", description="Colored roles aren't enabled on this server", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Check if the user has the manage server permission
        # ==================================================
        manager = False
        if ctx.author.guild_permissions.manage_guild:
            manager = True
        
        # ==================================================
        # If they want to change permissions
        # ==================================================
        if _one == "role":
            # ==================================================
            # Check if they input a role
            # ==================================================
            if _two == "":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a role by pinging the role", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Check if the user has the manage server permission
            # ==================================================
            if not manager:
                embed = oap.makeEmbed(title="Whoops!", description="You don't have the required permissions to toggle colored roles\nOnly users with the Manage Server permission can do this", ctx=ctx)
                return await ctx.send(embed=embed)
           
            # ==================================================
            # Check if they want to reset the role
            # ==================================================
            if _two == "reset":
                server_data["colored_roles"]["required_role"] = None
                oap.setJson(f"servers/{ctx.guild.id}", server_data)
                embed = oap.makeEmbed(title="Success!", description=f"A role is no longer required to make colored roles", ctx=ctx)
                await ctx.send(embed=embed)
                return oap.log(text=f"Removed the role requirement for colored roles", cog="Settings", color="yellow", ctx=ctx)

            # ==================================================
            # Get role id
            # Try to get the role object by id
            # ==================================================
            role_id = _two[3:-1]
            role = ctx.guild.get_role(int(role_id))

            # ==================================================
            # If the role doesnt exist
            # Say so
            # ==================================================
            if role == None:
                embed = oap.makeEmbed(title="Whoops!", description="I couldn't find that role", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Set value
            # Write data
            # Send output
            # Log to console
            # ==================================================
            server_data["colored_roles"]["required_role"] = int(role_id)
            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Required role has been changed to {role.name}", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text=f"Changed required role for colored role creation to {role.name}", cog="Settings", color="yellow", ctx=ctx)

        # ==================================================
        # If the server has a required role set
        # ==================================================
        has_required_role = True
        if server_data["colored_roles"]["required_role"]:
            has_required_role = False

            # ==================================================
            # Go through all the users roles to see if they have it
            # ==================================================
            for role in ctx.author.roles:
                if role.name == ctx.guild.get_role(server_data["colored_roles"]["required_role"]).name:
                    has_required_role = True

            # ==================================================
            # If they have the manage server permission
            # They can do it regardless
            # ==================================================
            if ctx.author.guild_permissions.manage_guild:
                has_required_role = True
        
        # ==================================================
        # Check if the role exists
        # And if theyre the owner
        # ==================================================
        server_role_exists = False
        server_role = None
        role_exists = False
        owns_role = False
        role_index = None
        for i in range(len(server_data["colored_roles"]["roles"])):
            if server_data["colored_roles"]["roles"][i]["name"] == _two:
                role_exists = True
                role_index = i
                server_role = ctx.guild.get_role(server_data["colored_roles"]["roles"][i]["id"])
                if server_role != None:
                    server_role_exists = True
                if server_data["colored_roles"]["roles"][i]["creator"] == ctx.author.id:
                    owns_role = True
        if manager:
            owns_role = True

        # ==================================================
        # If they want to create a role
        # ==================================================
        if _one == "create":
            # ==================================================
            # If they dont have a required role, send an error
            # ==================================================
            if not has_required_role:
                    embed = oap.makeEmbed(title="Whoops!", description="You don't have the required role to create colored roles", ctx=ctx)
                    return await ctx.send(embed=embed)

            # ==================================================
            # Check if they provided name and color values
            # ==================================================
            if _two == "":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a role name and color", ctx=ctx)
                return await ctx.send(embed=embed)

            if _three == "":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a role color", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Check if they gave a valid color
            # ==================================================
            color = _three
            if color.startswith("#"):
                color = color[1:]
            if len(color) != 6:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid color hex value", ctx=ctx)
                return await ctx.send(embed=embed)

            try:
                color = oap.hexToRGB(color)
                color = discord.Colour.from_rgb(color[0], color[1], color[2])
            except:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid color hex value", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Check if a role with the given name already exists
            # ==================================================
            if server_role_exists:
                embed = oap.makeEmbed(title="Whoops!", description="A role with that name already exists", ctx=ctx)
                return await ctx.send(embed=embed)
            
            # ==================================================
            # Create a role
            # Move it above the persons top role
            # Assign it to the person
            # Throw an error if permissions fail me
            # ==================================================
            try:
                where = "create the role"
                role = await ctx.guild.create_role(name=_two, colour=color, reason=f"Colored role created by {ctx.author.name}")

                for user_role in ctx.author.roles:
                    if user_role.color.value != 0:
                        top_user_role_position = user_role.position
                position = top_user_role_position + 1

                where = "give you the role"
                await ctx.author.add_roles(role, reason=f"Colored role created by {ctx.author.name}")
                where = "move the role up"
                await role.edit(position=position, reason=f"Colored role created by {ctx.author.name}")
            except:
                embed = oap.makeEmbed(title="Whoops!", description=f"I couldnt {where}\nMake sure I have the Manage Roles permission, and that I have a role above all other roles\n\n*(I know this is annoying, I wish it was different, but that's what discord requires)*", ctx=ctx)
                return await ctx.send(embed=embed)

            server_data["colored_roles"]["roles"].append({
                "name": role.name,
                "id": role.id,
                "creator": ctx.author.id
            })

            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Created a new role, \"{role.name}\", with a color of {_three}", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Created a new colored role", cog="Settings", color="yellow", ctx=ctx)
    
        # ==================================================
        # If they want to edit a role
        # ==================================================
        if _one == "edit":
            # ==================================================
            # If they dont have a require role, error
            # ==================================================
            if not has_required_role:
                    embed = oap.makeEmbed(title="Whoops!", description="You don't have the required role to create colored roles", ctx=ctx)
                    return await ctx.send(embed=embed)

            # ==================================================
            # Check if they gave role, setting, and value values
            # ==================================================
            if _two == "":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a role to edit", ctx=ctx)
                return await ctx.send(embed=embed)
            
            if _three == "":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter what you want to edit (name or color)", ctx=ctx)
                return await ctx.send(embed=embed)

            if _four == "":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter what you want the value to be", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Check if they gave valid arguments
            # ==================================================
            if _three not in ["name", "color"]:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter either name or color as the value to edit", ctx=ctx)
                return await ctx.send(embed=embed)

            if _three == "color":
                color = _four
                if color.startswith("#"):
                    color = color[1:]
                if len(color) != 6:
                    embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid color hex value", ctx=ctx)
                    return await ctx.send(embed=embed)

                try:
                    color = oap.hexToRGB(color)
                    color = discord.Colour.from_rgb(color[0], color[1], color[2])
                except:
                    embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid color hex value", ctx=ctx)
                    return await ctx.send(embed=embed)

            # ==================================================
            # Check if the role they gave actually exists
            # ==================================================
            if not role_exists:
                embed = oap.makeEmbed(title="Whoops!", description="I couldn't find a colored role with that name", ctx=ctx)
                return await ctx.send(embed=embed)
            
            # ==================================================
            # If they dont own the role
            # And dont have the manage server permission
            # Give them an error
            # ==================================================
            if not owns_role:
                embed = oap.makeEmbed(title="Whoops!", description="I couldn't find any roles you own with that name")
                return await ctx.send(embed=embed)
            
            # ==================================================
            # Apply changes
            # Throw an error if perms dont exist
            # ==================================================
            try:
                # ==================================================
                # Try to get the role by id
                # Return an error if i cant
                # ==================================================
                role = ctx.guild.get_role(server_data["colored_roles"]["roles"][role_index]["id"])

                if role == None:
                    embed = oap.makeEmbed(title="Whoops!", description="I couldn't find that role\nDid it get deleted?", ctx=ctx)
                    return ctx.send(embed=embed)

                # ==================================================
                # If theyre changing the name
                # ==================================================
                if _three == "name":
                    await role.edit(name=_four, reason=f"Colored role edited by {ctx.author.name}")
                    server_data["colored_roles"]["roles"][role_index]["name"] = _four
                
                # ==================================================
                # If theyre changing the color
                # ==================================================
                if _three == "color":
                    await role.edit(color=color, reason=f"Colored role edited by {ctx.author.name}")
            
            except:
                embed = oap.makeEmbed(title="Whoops!", description=f"I couldn't change the role {_three}\nMake sure I have the Manage Roles permission, and that I have a role above all other roles\n\n*(I know this is annoying, I wish it was different, but that's what discord requires)*", ctx=ctx)
                return await ctx.send(embed=embed)

            oap.setJson(f"servers/{ctx.author.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Changed {_two}'s {_three} to {_four}", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Created a new colored role", cog="Settings", color="yellow", ctx=ctx)
        
        # ==================================================
        # If they want to remove a role
        # ==================================================
        if _one == "delete":
            # ==================================================
            # Check if they gave arguments
            # ==================================================
            if _two == "":
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a role for me to delete", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Check if the colored role exists
            # ==================================================
            if not role_exists:
                embed = oap.makeEmbed(title="Whoops!", description="I couldn't find a colored role with that name", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Check if they own the role
            # ==================================================
            if not owns_role:
                embed = oap.makeEmbed(title="Whoops!", description="I couldn't find a role that you own with that name", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Delete the role
            # Remove the role from server data
            # Say if i got an error from any of that
            # ==================================================
            try:
                await server_role.delete(reason=f"{ctx.author.name} deleted a colored role")
                del server_data["colored_roles"]["roles"][role_index]
            except:
                embed = oap.makeEmbed(title="Whoops!", description="I couldnt delete the role\nMake sure I have the Manage Roles permission, and that I have a role above all other roles\n\n*(I know this is annoying, I wish it was different, but that's what discord requires)*", ctx=ctx)
                return await ctx.send(embed=embed)

            # ==================================================
            # Write server data
            # Send output
            # Log to console
            # ==================================================
            oap.setJson(f"servers/{ctx.author.id}", server_data)
            embed = oap.makeEmbed(title="Success!", description=f"Deleted the colored role \"{_two}\"", ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text="Created a new colored role", cog="Settings", color="yellow", ctx=ctx)


# ==================================================
# Cog Setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Settings", color="yellow")
    bot.add_cog(Settings(bot))
    reload(oap)
