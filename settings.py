from os import error
import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from importlib import reload
import emoji as em
import discord
import re


class Settings(commands.Cog, description="Settings, per-server or per-user"):
    def __init__(self, bot):
        self.abacus = bot
        self.cog_name = "Settings"
        self.data = oap.getJson("data")

    # ==================================================
    # Unload Event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="Settings", color="yellow")


    # ==================================================
    # Toggle delete invocation command 
    # ==================================================
    @commands.command(brief="Toggle whether or not to delete invocation messages", help="""\
        __**Required Permissions**__
        - Manage Server
        
        By default, Abacus doesn't delete invocation messages (the message with the command in it). If this is on, Abacus will delete those messages.
        
        __**Examples**__
        `>>toggle_delete_invocation`
        """)
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
            changed_to = "disabled"
            out = "I wont delete invocation messages."
        elif server_data.get("delete_invocation") in [False, None]:
            server_data["delete_invocation"] = True
            changed_to = "enabled"
            out = "I'll remove invocation messages."

        # ==================================================
        # Set data, send output, and log to console
        # ==================================================
        return await oap.give_output(
            embed_title=f"Alright!",
            embed_description=out,
            log_text=f"Invocation deletion {changed_to}",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data)

    
    # ==================================================
    # Poll settings command
    # ==================================================
    @commands.command(brief="Change default settings for the poll command", usage="[category] [setting]", help="""\
        __**Required Permissions**__
        - Manage Server
        
        Change the default settings for polls on this server.
        
        __**Examples**__
        `>>poll_settings emoji yes :thumbsup:`
        `>>poll_settings emoji no reset`
        `>>poll_settings emoji all reset`
        """)
    @commands.has_permissions(manage_guild=True)
    async def poll_settings(self, ctx, category="", *, value=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        examples = [
            "`>>poll_settings invocation`",
            "`>>poll_settings emoji yes reset`"
        ]

        categories = [
            "emoji",
            "invocation"
        ]

        # ==================================================
        # Arg checking
        # ==================================================
        if category == "" or category not in categories:
            return await oap.give_error(
                text=f"Please enter a valid category.",
                categories=categories,
                examples=examples,
                ctx=ctx)

        
        # ==================================================
        # If theyre changing emoji
        # ==================================================
        if category == "emoji":
            examples = [
                "`>>poll_settings emoji yes :thumbsup:`",
                "`>>poll_settings emoji all reset`"
            ]

            # ==================================================
            # Arg check the value argument
            # ==================================================
            if value == "" or value.split(" ")[0] not in ["yes", "no", "shrug", "all"]:
                return await oap.give_error(
                    text=f"Please enter a valid emoji type to change.",
                    categories=[
                        "yes",
                        "no",
                        "shrug",
                        "all"
                    ],
                    category_title="Types",
                    examples=examples,
                    ctx=ctx)

            if len(value.split(" ")) == 1:
                return await oap.give_error(
                    text=f"Please enter an emoji to change to, or \"reset\".",
                    examples=examples,
                    ctx=ctx)

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
                    return await oap.give_error(
                        text=f"That emoji isn't from this server.\nSorry!",
                        ctx=ctx)

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
                    out = f"The default {which_emoji} emoji has been reset."
                else:
                    data[which_emoji] = emoji
                    out = f"The default {which_emoji} emoji has been set to {emoji}."
            else:
                if emoji == "reset":
                    data = {
                        "yes": "",
                        "no": "",
                        "shrug": ""
                    }
                    out = f"All default emoji have been reset."
                else:
                    data = {
                        "yes": emoji,
                        "no": emoji,
                        "shrug": emoji
                    }
                    out = f"All default emoji have been set to {emoji}."

            # ==================================================
            # Set data, send ouput, log to console
            # ==================================================
            server_data["poll"] = data

            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description={out},
                log_text=f"Changed {which_emoji} default poll emoji to {emoji}",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data)

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
                    out = "I'll no longer delete poll invocation messages."
                    value = "Disabled"
                else:
                    data["delete_invocation"] = True
                    out = "I'll delete poll invocation messages."
                    value = "Enabled"
            else:
                data["delete_invocation"] = False
                out = "I'll no longer delete poll invocation messages."
                value = "Disabled"

            # ==================================================
            # Set data, send output, log to console
            # ==================================================
            server_data["poll"] = data

            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=out,
                log_text=f"{value} poll invocation deletion",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data)


    # ==================================================
    # User settings command
    # ==================================================
    @commands.command(brief="Change your user settings", usage="[category] [value]", help="""\
        Change your user-specific settings.

        __**Examples**__
        `>>user_settings color`
        `>>user_settings color 2083ff`
        `>>user_settings color reset`
        """)
    async def user_settings(self, ctx, category="", *, input=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        user_data = oap.getJson(f"users/{ctx.author.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        examples = [
            "`>>user_settings color 2060FF`"
        ]

        categories = [
            "color"
        ]
    
        # ==================================================
        # Arg checking
        # ==================================================
        if category not in categories:
            return await oap.give_error(
                text=f"Please enter a valid category.",
                categories=categories,
                category_title="Categories",
                examples=examples,
                ctx=ctx)

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
                    return await oap.give_output(
                        embed_title=f"Alright!",
                        embed_description=f"Your color is {hex(user_data['color'])}",
                        ctx=ctx)
                else:
                    return await oap.give_output(
                        embed_title=f"Whoops!",
                        embed_description=f"\
                            You don't have a color yet!\n\
                            Set one with `>>user_settings color [hex code]`.",
                        ctx=ctx)

            # ==================================================
            # Check if they input "reset"
            # If so, just delete their set color
            # Then send output and log to console
            # ==================================================
            if input == "reset":
                del user_data["color"]

                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"Your color has been reset.",
                    log_text=f"Reset their user color",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data,
                    data_type="user")

            # ==================================================
            # Get rid of any starting hashtag
            # And check if they gave a valid length color
            # ==================================================
            if input.startswith("#"):
                input = input[1:]
            if len(input) != 6:
                return await oap.give_error(
                    text=f"Please enter a valid hex code for your color.",
                    examples=examples,
                    ctx=ctx)

            # ==================================================
            # Try making the color an integer
            # If it doesnt work, say so
            # ==================================================
            try:
                color = int(f"0x{input}", 16)
            except:
                return await oap.give_error(
                    text=f"Please enter a valid hex code for your color.",
                    examples=examples,
                    ctx=ctx)

            # ==================================================
            # Set their data
            # Send output
            # Log to console
            # ==================================================
            user_data["color"] = color

            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=f"Your color has been set to {input}.",
                log_text=f"Changed their user color to 0x{input}",
                cog=self.cog_name,
                ctx=ctx,
                data=user_data,
                data_type="user")


    # ==================================================
    # Hall of fame and shame config
    # ==================================================
    @commands.command(brief="Change hall of fame and shame settings", usage="[fame, shame, or message] [setting] [value]", help="""\
        __**Required Permissions**__
        - Manage Server
        
        Change the settings for hall of fame and hall of shame.
        
        __**What?**__
        - The hall of fame and hall of shame are places where messages will get sent, if given a specific amount of reactions.
        - By default, if a message gets four ⬆️ reactions, it will be sent in a designated hall of fame channel (if there is one), and the opposite for ⬇️.
        
        __**Emoji**__
        - Change the emoji that users must react with.
        `>>hall_settings fame emoji :thumbsup:`
        `>>hall_settings shame emoji reset`
        
        __**Requirement**__
        - Change the amount of each reaction required for the message to be sent in a channel.
        `>>hall_settings fame requirement 12`
        `>>hall_settings shame requirement reset`
        
        __**Channel**__
        - Change which channel the bot should send messages in when they get enough reactions.
        `>>hall_settings fame channel #hall-of-fame`
        `>>hall_settings shame channel reset`
        
        __**Announcement Messages**__
        - Change what message the bot will send when a user gets enough reactions.
        `>>hall_settings fame message [user] is super cool!`
        `>>hall_settings fame removal_message [user] is no longer cool`
        `>>hall_settings shame message [user] is totally lame :/`
        `>>hall_settings shame removal_message reset`
        
        __**Message**__
        - Change the message that gets sent in the hall of fame or shame.
        `>>hall_settings message "[[channel]] **[user]**: [message]
        ([attachments])"`
        `>>hall_settings message reset`
        """)
    @commands.has_permissions(manage_guild=True)
    async def hall_settings(self, ctx, which="", setting="", *, input=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        examples = [
            "`>>hall_settings fame`",
            "`>>hall_settings shame`",
            "`>>hall_settings message`"
        ]
    
        # ==================================================
        # Argument checking
        # ==================================================
        if which not in ["fame", "shame", "message"]:
            return await oap.give_error(
                text=f"\
                    Please enter either fame or shame as the hall you want to change.\n\
                    You can also enter \"message\" to change how the message is formatted when someone gets put in a hall.",
                examples=examples,
                ctx=ctx)

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
                return await oap.give_error(
                    text=f"\
                        If you wish to change this, enter a message surrounded by quotes.\n\
                        You can use discord's formatting, and variables such as [user], [message], [attachments], and [channel].",
                    examples=[
                        "`>>poll_settings message \"[user] // [message]\"`"
                    ],
                    ctx=ctx)

            # ==================================================
            # If the data doesnt exist, use defaults
            # ==================================================
            if not server_data.get("halls"):
                server_data["halls"] = default

            # ==================================================
            # Store the old value
            # Change the value in the server data
            # ==================================================
            old_value = server_data.get("message")
            server_data["message"] = setting

            embed = oap.makeEmbed(
                title=f"Alright!",
                description=f"\
                    Successfully changed the default message format.\n\
                    *If this doesn't look correct, make sure you put the message in quotes!*",
                ctx=ctx
            )
            
            embed.add_field(
                name=f"Old Value",
                value=f"{old_value}",
                inline=False
            )

            embed.add_field(
                name=f"New Value",
                value=f"{input}",
                inline=False
            )
            
            return await oap.give_output(
                embed=embed,
                log_text=f"Changed the hall message format",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        # ==================================================
        # If they didnt input a setting to change
        # Just give them current settings
        # ==================================================
        if setting == "":
            embed = oap.makeEmbed(
                title=f"Current Hall of {which.title()} Settings",
                description=f"*Any of these can be changed.*",
                ctx=ctx
            )
            
            embed.add_field(name=f"Emoji", value=server_data["halls"][which]["emoji"], inline=True)
            embed.add_field(name=f"Requirement", value=server_data["halls"][which]["requirement"], inline=True)
            embed.add_field(name=f"Channel", value=server_data["halls"][which]["channel"], inline=True)
            embed.add_field(name=f"Message", value=server_data["halls"][which]["message"], inline=True)
            embed.add_field(name=f"Removal Message", value=server_data["halls"][which]["removal_message"], inline=True)
            
            return await oap.give_output(
                embed=embed,
                log_text=f"Got hall of {which} settings",
                cog=self.cog_name,
                ctx=ctx
            )

        # ==================================================
        # Set new examples
        # ==================================================
        examples = [
            "`>>hall_settings fame emoji :thumbsup:`",
            "`>>hall_settings fame requirement 7`",
            "`>>hall_settings fame channel #hall-of-fame`",
            "`>>hall_settings fame message [user] is one of the cool kids now`",
            "`>>hall_settings fame removal_message [user] isn't cool anymore...`"
        ]

        # ==================================================
        # If they *did* give a setting to change
        # Check if it's a valid setting
        # ==================================================
        settings = [
            "emoji",
            "requirement",
            "channel",
            "message",
            "removal_message"
        ]

        if setting not in settings:
            return await oap.give_error(
                text=f"Please enter a valid setting to change.",
                categories=settings,
                category_title="Settings",
                examples=examples,
                ctx=ctx
            )

        # ==================================================
        # Check if the value they gave is valid
        # ==================================================
        if setting == "emoji":
            if input == "reset":
                input = "⬆️" if which == "fame" else "⬇️"

            elif input not in em.UNICODE_EMOJI and not re.match(r"(:([^\s:]+):(?!\d))|(<(:|(a:))([^\s<>]+):(\d{18})>)", input):
                return await oap.give_error(
                    text=f"Please enter a valid emoji.",
                    examples=[
                        "`>>hall_settings fame emoji :thumbsup:`",
                        "`>>hall_settings shame emoji reset`"
                    ],
                    ctx=ctx
                )


        if setting == "requirement":
            examples = [
                "`>>hall_settings fame requirement 5`",
                "`>>hall_settings shame requirement reset`"
            ]

            if input == "reset":
                input = 4
            try:
                input = int(input)
                if input < 1:
                    return await oap.give_error(
                        text=f"Please enter a positive, nonzero integer.",
                        examples=examples,
                        ctx=ctx
                    )
            except:
                return await oap.give_error(
                    text=f"Please enter a positive, nonzero integer.",
                    examples=examples,
                    ctx=ctx
                )


        if setting == "channel":
            if input == "reset":
                input = "None"
            if not re.match(r"(<#(\d+)>)", input) and input != "None":
                return await oap.give_error(
                    text=f"Please enter a valid channel.",
                    examples=[
                        "`>>hall_settings fame channel #hall-of-fame`",
                        "(tag the channel you wish to use)"
                    ],
                    ctx=ctx
                )


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
        embed = oap.makeEmbed(
            title=f"Alright!",
            description=f"Successfully changed the hall of {which}'s {setting}.",
            ctx=ctx
        )
        
        embed.add_field(
            name=f"Old Value",
            value=f"{old_value}",
            inline=False
        )

        embed.add_field(
            name=f"New Value",
            value=f"{input}",
            inline=False
        )
        
        return await oap.give_output(
            embed=embed,
            log_text=f"",
            cog=self.cog_name,
            ctx=ctx,
            data=server_data
        )

    
    # ==================================================
    # Autoresponders settings
    # ==================================================
    @commands.command(brief="Change autoresponder settings", help="""\
        __**Required Permissions**__
        - Manage Server
        
        Add, remove, and edit autoresponders for this server.
        
        __**Types**__
        - Autoresponders can have a type of "word", "anywhere", "beginning", or "end".
        - "word" means it will only respond if the trigger is a word by itself (not contained within another word)
        - "anywhere" will respond if the trigger is anywhere in the message.
        - "beginning" and "end" will only respond if the trigger is at the beginning or end of the message.
        
        __**Examples**__
        `>>autoresponders toggle`
        `>>autoresponders list`
        `>>autoresponders add word bro bro!!`
        `>>autoresponders remove 1`
        `>>autoresponders edit 1 trigger dude`
        """)
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
            value = "on" if server_data["autoresponder"] else "off"

            # ==================================================
            # Write the data
            # Send output
            # Log to console
            # ==================================================
            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=f"Autoresponders have been toggled {value} for this server.",
                log_text=f"Toggled autoresponders {value}",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data,
                data_type="server"
            )

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
                return await oap.give_error(
                    text=f"Please enter a valid autoresponder type.",
                    categories=[
                        "word",
                        "anywhere",
                        "beginning",
                        "end"
                    ],
                    category_title="Types",
                    examples=[
                        "`>>autoresponder add word bruh \"bruh moment\"`",
                        "`>>autoresponder add anywhere sus \"among us\"`"
                    ],
                    ctx=ctx
                )

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
            embed = oap.makeEmbed(
                title=f"Alright!",
                description=f"\
                    Autoresponder added!\n\
                    *If these don't look how you wanted them to, make sure you put the trigger and response in quotation marks!*",
                ctx=ctx
            )
            
            embed.add_field(
                name=f"Trigger",
                value=trigger,
                inline=True
            )

            embed.add_field(
                name=f"Response",
                value=response,
                inline=True
            )
            
            return await oap.give_output(
                embed=embed,
                log_text=f"",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        # ==================================================
        # If they're removing an autoresponder
        # Send an error if the server doesnt have any
        # ==================================================
        if which == "remove":
            if not server_data.get("autoresponders") or len(server_data.get("autoresponders")) == 0:
                return await oap.give_error(
                    text=f"\
                        This server doesn't have any autoresponders.\n\
                        Try adding some with `>>autoresponder add`!",
                    ctx=ctx
                )

            # ==================================================
            # Try to convert input to an int
            # If it fails, send em an error
            # ==================================================
            try:
                num = int(num)
            except:
                return await oap.give_error(
                    text=f"\
                        That wasn't a valid autoresponder ID.\n\
                        Valid IDs will always be a number!\n\
                        Get all autoresponders with `>>autoresponders list`.",
                    ctx=ctx
                )

            # ==================================================
            # Check if the server actually has as many autoresponders as specified
            # ==================================================
            if len(server_data["autoresponders"]) < num:
                return await oap.give_error(
                    text=f"\
                        I couldn't find an autoresponder with that ID!\n\
                        Get all autoresponders with `>>autoresponders list`.",
                    ctx=ctx
                )

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
            embed = oap.makeEmbed(
                title=f"Alright!",
                description=f"Autoresponder removed!",
                ctx=ctx
            )
            
            embed.add_field(
                name=f"Trigger",
                value=deleted_auto["trigger"],
                inline=True
            )

            embed.add_field(
                name=f"Response",
                value=deleted_auto["response"],
                inline=True
            )
            
            return await oap.give_output(
                embed=embed,
                log_text=f"Removed an autoresponder",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )

        # ==================================================
        # If they're listing autoresponders
        # Send error if the server doesnt have any
        # ==================================================
        if which == "list":
            if not server_data.get("autoresponders") or len(server_data.get("autoresponders")) == 0:
                return await oap.give_error(
                    text=f"\
                        This server doesn't have any autoresponders!\n\
                        Try adding some with `>>autoresponders add`.",
                    ctx=ctx
                )

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
            return await oap.give_output(
                embed_title=f"all autoresponders for {ctx.guild.name}".title(),
                embed_description=embed_description,
                log_text=f"Listed all autoresponders",
                cog=self.cog_name,
                ctx=ctx
            )


    # ==================================================
    # Colored roles
    # ==================================================
    @commands.command(brief="Manage colored roles", help="""\
        *For this to work, I have to have a role above every other role in the server. This is a discord limitation, unfortunately*
        
        __**Required Permissions**__
        **Toggle**: Manage Server
        **Change Required Role**: Manage Server
        **Create/Edit/Delete**: Variable
        
        Toggle, create, edit, and delete custom colored roles. This lets people give themselves custom colors without giving them new permissions and without any hassle.
        
        __**Toggle**__
        Toggle colored roles off or on for this server. By default, anyone can create, edit, and delete colored roles - but only ones theyve created.
        `>>colored_roles toggle`
        
        __**Permissions**__
        Anyone with the Manage Server permission can set who can use this command. This allows you to set a role, and any user that doesn't have that role won't be able to use this command.
        `>>colored_roles role @Colorful`
        `>>colored_roles role reset`
        
        __**Create**__
        Create a role with a specific name and hex color. I'll automatically give you the role, and place it above your current role. You cannot name a role something that already exists.
        `>>colored_role create Blue 4060ff`
        `>>colored_role create Green 22ff67`
        
        __**Edit**__
        Edit a pre-existing role that you've created. If you have the Manage Server permission, you can edit any created role.
        `>>colored_role edit Blue name Red`
        `>>colored_role edit Red color e05020`
        
        __**Delete**__
        Remove a role that you've created. If you have the Manage Server permission, you can remove any created role.
        `>>colored_role delete Red`
        """, aliases=["colored_role"])
    async def colored_roles(self, ctx, _one="", _two="", _three="", _four=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        actions = [
            "toggle",
            "create",
            "edit",
            "delete",
            "role"
        ]

        examples = [
            "`>>colored_roles toggle`",
            "`>>colored_roles create Blue 4060FF`",
            "`>>colored_roles edit Blue color 0080EE`",
            "`>>colored_roles delete Blue`",
            "`>>colored_roles role @Colorful`"
        ]

        # ==================================================
        # Argument checking
        # ==================================================
        if _one not in actions:
            return await oap.give_error(
                text=f"Please enter a valid action!",
                categories=actions,
                category_title="Actions",
                examples=examples,
                ctx=ctx
            )

        default = {
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
            server_data["colored_roles_enabled"] = False

        # ==================================================
        # If they want to toggle colored roles
        # ==================================================
        if _one == "toggle":
            # ==================================================
            # Check if the user has the manage server permission
            # ==================================================
            if not ctx.author.guild_permissions.manage_guild:
                return await oap.give_error(
                    text=f"\
                        You don't have the require permissions to toggle colored roles!\n\
                        Only users with the Manage Server permission can do that.",
                    ctx=ctx
                )

            # ==================================================
            # Change the value in server_data
            # Write the data to the servers file
            # Send output
            # Log to console
            # ==================================================
            server_data["colored_roles_enabled"] = False if server_data["colored_roles_enabled"] == True else True

            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=f"Colored roles have been {'enabled' if server_data['colored_roles_enabled'] else 'disabled'} for this server.",
                log_text=f"Toggled role colors to {server_data['colored_roles_enabled']}",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data,
                data_type="server"
            )

        # ==================================================
        # If the server has colored roles disabled
        # Send an error
        # ==================================================
        if not server_data["colored_roles_enabled"]:
            return await oap.give_error(
                text=f"Colored roles aren't enabled on this server.",
                ctx=ctx
            )

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
                return await oap.give_error(
                    text=f"Please enter a role, by pinging the role.",
                    examples=[
                        "`>>colored_roles role @Colorful`"
                    ],
                    ctx=ctx
                )

            # ==================================================
            # Check if the user has the manage server permission
            # ==================================================
            if not manager:
                return await oap.give_error(
                    text=f"\
                        You don't have the required permissions to change the required role!\n\
                        Only users with the Manage Server permission can do that.",
                    ctx=ctx
                )
           
            # ==================================================
            # Check if they want to reset the role
            # ==================================================
            if _two == "reset":
                server_data["colored_roles"]["required_role"] = None

                return await oap.give_output(
                    embed_title=f"Alright!",
                    embed_description=f"A role is no longer required to create colored roles.",
                    log_text=f"Removed the role requirement for colored roles",
                    cog=self.cog_name,
                    ctx=ctx,
                    data=server_data,
                    data_type="server"
                )

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
                return await oap.give_error(
                    text=f"\
                        I couldn't find that role!\n\
                        Make sure to ping the role.",
                    ctx=ctx
                )

            # ==================================================
            # Set value
            # Write data
            # Send output
            # Log to console
            # ==================================================
            server_data["colored_roles"]["required_role"] = int(role_id)

            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=f"The required role has been changed to {role.name}",
                log_text=f"Changed required role for colored roles to {role.name}",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data,
                data_type="server"
            )

        # ==================================================
        # If they want to list colored roles
        # ==================================================
        if _one == "list":
            owned_roles = []
            for role in server_data["colored_roles"]["roles"]:
                if role["creator"] == ctx.author.id or manager:
                    manager_addition = f" (<!{role['id']}>)"
                    owned_roles.append(f"<!@{role['id']}>{manager_addition if manager else ''}")

            return await oap.give_output(
                embed_title=f"all roles accessible by {ctx.author.mention}",
                embed_description=("\n".join(owned_roles) if len(owned_roles) > 0 else "You don't own any roles!"),
                log_text=f"Listed accessible colored roles",
                cog=self.cog_name,
                ctx=ctx
            )

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
            examples = [
                "`>>colored_roles create Blue 2040FF`"
            ]

            # ==================================================
            # If they dont have a required role, send an error
            # ==================================================
            if not has_required_role:
                return await oap.give_error(
                    text=f"You don't have the required role to create colored roles!",
                    ctx=ctx
                )

            # ==================================================
            # Check if they provided name and color values
            # ==================================================
            if _two == "":
                return await oap.give_error(
                    text=f"Please enter a role name and color.",
                    examples=examples,
                    ctx=ctx
                )

            if _three == "":
                return await oap.give_error(
                    text=f"Please enter a role color.",
                    examples=examples,
                    ctx=ctx
                )

            # ==================================================
            # Check if they gave a valid color
            # ==================================================
            color = _three
            if color.startswith("#"):
                color = color[1:]
            if len(color) != 6:
                return await oap.give_error(
                    text=f"Please enter a valid color hex code.",
                    examples=examples,
                    ctx=ctx
                )

            try:
                color = oap.hexToRGB(color)
                color = discord.Colour.from_rgb(color[0], color[1], color[2])
            except:
                return await oap.give_error(
                    text=f"Please enter a valid color hex code.",
                    examples=examples,
                    ctx=ctx
                )

            # ==================================================
            # Check if a role with the given name already exists
            # ==================================================
            if server_role_exists:
                return await oap.give_error(
                    text=f"A role with that name already exists!",
                    ctx=ctx
                )
            
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
                return await oap.give_error(
                    text=f"\
                        I couldn't {where}!\n\
                        Make sure I have the Manage Roles permission, and that I have a role above all other roles.\n\
                        \n\
                        *(I know this is annoying, but that's what discord requires.)*",
                    ctx=ctx
                )

            server_data["colored_roles"]["roles"].append({
                "name": role.name,
                "id": role.id,
                "creator": ctx.author.id
            })

            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=f"Created a new role, \"{role.name}\", with a color of {_three}",
                log_text=f"Created a new colored role",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data,
                data_type="server"
            )
    
        # ==================================================
        # If they want to edit a role
        # ==================================================
        if _one == "edit":
            examples = [
                "`>>colored_roles edit Blue name Red`",
                "`>>colored_roles edit Red color FF8020`"
            ]

            # ==================================================
            # If they dont have a require role, error
            # ==================================================
            if not has_required_role:
                return await oap.give_error(
                    text=f"You don't have the required role to create colored roles!",
                    ctx=ctx
                )

            # ==================================================
            # Check if they gave role, setting, and value values
            # ==================================================
            if _two == "":
                return await oap.give_error(
                    text=f"Please enter a role to edit.",
                    examples=examples,
                    ctx=ctx
                )
            
            if _three == "":
                return await oap.give_error(
                    text=f"Please enter what you want to edit. (name or color)",
                    examples=examples,
                    ctx=ctx
                )

            if _four == "":
                return await oap.give_error(
                    text=f"Please enter what you want the value to be.",
                    examples=examples,
                    ctx=ctx
                )

            # ==================================================
            # Check if they gave valid arguments
            # ==================================================
            if _three not in ["name", "color"]:
                return await oap.give_error(
                    text=f"Please enter either name or color as the value to edit!",
                    examples=examples,
                    ctx=ctx
                )

            if _three == "color":
                color = _four
                if color.startswith("#"):
                    color = color[1:]
                if len(color) != 6:
                    return await oap.give_error(
                        text=f"Please enter a valid color hex code!",
                        examples=[
                            "`>>colored_roles edit Red color FF8020`"
                        ],
                        ctx=ctx
                    )

                try:
                    color = oap.hexToRGB(color)
                    color = discord.Colour.from_rgb(color[0], color[1], color[2])
                except:
                    return await oap.give_error(
                        text=f"Please enter a valid color hex code!",
                        examples=[
                            "`>>colored_roles edit Red color FF8020`"
                        ],
                        ctx=ctx
                    )

            # ==================================================
            # Check if the role they gave actually exists
            # ==================================================
            if not role_exists:
                return await oap.give_error(
                    text=f"\
                        I couldn't find a colored role with that name!\n\
                        List colored roles with `>>colored_roles list`.",
                    ctx=ctx
                )
            
            # ==================================================
            # If they dont own the role
            # And dont have the manage server permission
            # Give them an error
            # ==================================================
            if not owns_role:
                return await oap.give_error(
                    text=f"\
                        I coudn't find any roles you own with that name!\n\
                        List your colored roles with `>>colored_roles list`.",
                    ctx=ctx
                )
            
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
                    return await oap.give_error(
                        text=f"\
                            I couldn't find that role!\n\
                            Did it get deleted?",
                        ctx=ctx
                    )

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
                return await oap.give_error(
                    text=f"\
                        I couldn't change the role {_three}!\n\
                        Make sure I have the Manage Roles permission, and that I have a role above all other roles.\n\
                        \n\
                        *(I know this is annoying, but that's what discord requires.)*",
                    ctx=ctx
                )

            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=f"Changed {_two}'s {_three} to {_four}",
                log_text=f"Created a new colored role",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data,
                data_type="server"
            )
        
        # ==================================================
        # If they want to remove a role
        # ==================================================
        if _one == "delete":
            examples = [
                "`>>colored_roles delete Blue`"
            ]

            # ==================================================
            # Check if they gave arguments
            # ==================================================
            if _two == "":
                return await oap.give_error(
                    text=f"Please enter a role for me to delete!",
                    examples=examples,
                    ctx=ctx
                )

            # ==================================================
            # Check if the colored role exists
            # ==================================================
            if not role_exists:
                return await oap.give_error(
                    text=f"\
                        I couldn't find a colored role with that name!\n\
                        List colored roles with `>>colored_roles list`.",
                    ctx=ctx
                )

            # ==================================================
            # Check if they own the role
            # ==================================================
            if not owns_role:
                return await oap.give_error(
                    text=f"You can't delete that role!",
                    ctx=ctx
                )

            # ==================================================
            # Delete the role
            # Remove the role from server data
            # Say if i got an error from any of that
            # ==================================================
            try:
                await server_role.delete(reason=f"{ctx.author.name} deleted a colored role")
                del server_data["colored_roles"]["roles"][role_index]
            except:
                return await oap.give_error(
                    text=f"\
                        I couldn't delete that role!\n\
                        Make sure I have the Manage Roles permission, and that I have a role above all other roles.\n\
                        \n\
                        *(I know this is annoying, but that's what discord requires.)*",
                    ctx=ctx
                )

            # ==================================================
            # Write server data
            # Send output
            # Log to console
            # ==================================================
            return await oap.give_output(
                embed_title=f"Alright!",
                embed_description=f"Deleted the colored role \"{_two}\"!",
                log_text=f"Deleted a colored role",
                cog=self.cog_name,
                ctx=ctx,
                data=server_data
            )


    # ==================================================
    # Remade Server Settings
    # ==================================================
    @commands.command(brief="Change server-wide settings", help="i dunno lol ill write this later", enabled=False)
    async def server_settings(self, ctx):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        def id_check(message):
            return message.author.id == ctx.author.id

        # ==================================================
        # Make a big embed with all server settings and values
        # ==================================================
        embed = oap.makeEmbed(title="Alright!", description=f"""\
            Here are the current settings for {ctx.guild.name}.

            **Delete Command Invocation:** {server_data.get("delete_invocation")}
            **Autoresponders:** {"Enabled" if server_data.get("autoresponder") == True else "Disabled"}

            __**Colored Roles ({("Enabled" if server_data["colored_roles"]["enabled"] else "Disabled") if server_data.get("colored_roles") else "Disabled"})**__
            **Required Role:** {(ctx.guild.get_role(server_data["colored_roles"]["required_role"]).mention if server_data["colored_roles"]["required_role"] else "None") if server_data.get("colored_roles") else "None"}

            __**Halls**__
            **Fame:** {("Enabled" if server_data["halls"]["fame"]["channel"] != None else "Disabled") if server_data.get("halls") else "Disabled"}
            **Shame:** {("Enabled" if server_data["halls"]["shame"]["channel"] != None else "Disabled") if server_data.get("halls") else "Disabled"}

            __**Valid Toggles**__
            - Invocation
            - Autoresponders
            - Colored roles

            __**Valid Categories**__
            - Autoresponders
            - Colored roles
            - Halls
            - Polls

            Respond to this message with a toggle and I'll toggle it for you!
            `toggle invocation`

            Respond to this message with a category and I'll give you more detailed information!
            `category autoresponders`

            *Otherwise, I'll ignore your message*
            """, ctx=ctx)
        settings_message = await ctx.send(embed=embed)

        # ==================================================
        # Wait for the next message from the original author
        # ==================================================
        response_message = await self.abacus.wait_for("message", check=id_check)
        response = response_message.content.lower()

        # ==================================================
        # If the message starts with toggle
        # Check if the following word(s) fit a toggleable setting
        # If not, throw error
        # If so, toggle it
        # ==================================================
        if response.startswith("toggle"):
            if response.split("toggle ")[1] not in ["invocation", "autoresponders", "colored roles"]:
                embed = oap.makeEmbed(
title="Whoops!",
description="I couldn't find a toggle with that name.\nMake sure you spelt it correctly!",
ctx=ctx)
                return await ctx.send(embed=embed)

            if response.endswith("invocation"):
                server_data["delete_invocation"] = False if server_data.get("delete_invocation") == True else True
                out = "Invocation deletion has"
                value = "on" if server_data["delete_invocation"] == True else "off"

            if response.endswith("autoresponders"):
                server_data["autoresponder"] = False if server_data.get("autoresponder") == True else True
                out = "Autoresponders have"
                value = "on" if server_data["autoresponder"] == True else "off"

            if response.endswith("colored roles"):
                if not server_data.get("colored_roles"):
                    server_data["colored_roles"] = {
                        "enabled": False,
                        "required_role": None,
                        "roles": []
                    }

                server_data["colored_roles"]["enabled"] = False if server_data["colored_roles"]["enabled"] == True else True
                out = "Colored roles have"
                value = "on" if server_data["colored_roles"]["enabled"] == True else "off"

            oap.setJson(f"servers/{ctx.guild.id}", server_data)
            embed = oap.makeEmbed(
title="Success!",
description=f"{out} been toggled {value} for {ctx.guild.name}",
ctx=ctx)
            await ctx.send(embed=embed)
            return oap.log(text=f"Toggled {response.split('toggle ')[1]} {value}", cog="Settings", color="yellow", ctx=ctx)


        # ==================================================
        # If the message starts with category
        # Check if they gave a valid category
        # Give them information on that category
        # ==================================================
        # if response.startswith("category"):
        #     category = response.split("category ")[1]
        #     if category not in ["autoresponders", "colored roles", "halls", "polls"]:
        #         embed = oap.makeEmbed(
                    # title="Whoops!",
                    # description="That wasn't a valid category!\nDid you spell it right?",
                    # ctx=ctx)
        #         return ctx.send(embed=embed)


# ==================================================
# Cog Setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Settings", color="yellow")
    bot.add_cog(Settings(bot))
    reload(oap)
