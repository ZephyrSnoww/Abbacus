import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from importlib import reload
import discord
import re


class Events(commands.Cog):
    def __init__(self, bot):
        self.abacus = bot
        self.data = oap.getJson("data")

    # ==================================================
    # Unload event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="Events", color="magenta")


    # ==================================================
    # Reaction changing function
    # ==================================================
    async def reaction_event(self, payload):
        # ==================================================
        # Get server data
        # Get server
        # Get channel
        # Get message
        # Turn emoji into a string (unicode or custom)
        # ==================================================
        server_data = oap.getJson(f"servers/{payload.guild_id}")
        guild = await self.abacus.fetch_guild(payload.guild_id)
        channel = await self.abacus.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emoji = str(payload.emoji)
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
        # Check if data exists
        # If it doesnt, just fill defaults
        # ==================================================
        if not server_data.get("halls"):
            server_data["halls"] = default

        # ==================================================
        # Check if the emoji matches the servers fame/shame emoji
        # Check if the reaction is from a bot
        # Check if the message starts with >>poll
        # (Ignore the reaction if any of the above are true)
        # ==================================================
        if emoji != server_data["halls"]["fame"]["emoji"] and emoji != server_data["halls"]["shame"]["emoji"]:
            return
        elif message.content.startswith(">>poll"):
            return

        if payload.event_type == "REACTION_ADD":
            if payload.member.bot:
                return

        # ==================================================
        # Get the given hall
        # Get the halls requirement
        # ==================================================
        hall = "fame" if emoji == server_data["halls"]["fame"]["emoji"] else "shame"
        requirement = server_data["halls"][hall]["requirement"]

        # ==================================================
        # Check if the hall has a channel set
        # If not, ignore the reaction
        # ==================================================
        if server_data["halls"][hall]["channel"] == None:
            return

        # ==================================================
        # Count how many reactions there are
        # Get the total score for the message
        # ==================================================
        fame_count = 0
        shame_count = 0
        for reaction in message.reactions:
            if str(reaction.emoji) == server_data["halls"]["fame"]["emoji"]:
                fame_count = reaction.count
            if str(reaction.emoji) == server_data["halls"]["shame"]["emoji"]:
                shame_count = reaction.count

        score = fame_count - shame_count

        # ==================================================
        # If the score meets the requirement
        # Add the message to the servers list of messages
        # Announce and send in both channels
        # ==================================================
        if score >= requirement:
            if not server_data.get("sent_hall_messages"):
                server_data["sent_hall_messages"] = []
            
            # ==================================================
            # Check if the message is already in a hall
            # If so, just update the score
            # ==================================================
            in_hall = False
            for i in range(len(server_data["sent_hall_messages"])):
                if server_data["sent_hall_messages"][i]["id"] == message.id:
                    server_data["sent_hall_messages"][i]["score"] = score
                    in_hall = True
                
            if score == requirement:
                in_hall = False

            # ==================================================
            # Otherwise, add it to the list
            # Announce the addition
            # And send it in the correct hall
            # ==================================================
            if not in_hall:
                # ==================================================
                # Get the hall channel
                # Format the output message
                # ==================================================
                hall_channel = await self.abacus.fetch_channel(int(server_data["halls"][hall]["channel"][2:-1]))
                output = server_data["halls"][hall]["message"]
                output = re.sub(r"\[user\]", f"{message.author.name}", output)
                output = re.sub(r"\[attachments\]", "\n".join([attachment.url for attachment in message.attachments]), output)
                output = re.sub(r"\[channel\]", f"{str(channel)}", output)

                # ==================================================
                # Format the message to be sent in the hall
                # ==================================================
                output2 = server_data["halls"]["message"]
                output2 = re.sub(r"\[user\]", f"{message.author.name}", output2)
                output2 = re.sub(r"\[attachments\]", "\n".join([attachment.url for attachment in message.attachments]), output2)
                output2 = re.sub(r"\[channel\]", f"{str(channel)}", output2)
                output2 = re.sub(r"\[message\]", f"{message.content}", output2)
                # output = re.sub(r"", f"", output)

                # ==================================================
                # Send and log
                # ==================================================
                await channel.send(output)
                hall_message = await hall_channel.send(output2)

                server_data["sent_hall_messages"].append({
                    "id": message.id,
                    "hall": hall,
                    "author": message.author.id,
                    "original_channel": channel.id,
                    "score": score,
                    "hall_id": hall_message.id
                })
                oap.setJson(f"servers/{guild.id}", server_data)
                return oap.log(text=f"A message got to the hall of {hall}", cog="Events", color="magenta")

        # ==================================================
        # If the score doesnt meet the requirement
        # Check if the message is in a hall
        # If it is, remove it
        # Send output
        # ==================================================
        if score < requirement:
            if server_data.get("sent_hall_messages"):
                for sent_message in server_data["sent_hall_messages"]:
                    if sent_message["id"] == message.id:
                        hall_channel = await self.abacus.fetch_channel(int(server_data["halls"][sent_message["hall"]]["channel"][2:-1]))
                        hall_message = await hall_channel.fetch_message(sent_message["hall_id"])

                        # ==================================================
                        # Format removal message
                        # ==================================================
                        output = server_data["halls"][sent_message["hall"]]["removal_message"]
                        output = re.sub(r"\[user\]", f"{message.author.name}", output)
                        output = re.sub(r"\[attachments\]", "\n".join([attachment.url for attachment in message.attachments]), output)
                        output = re.sub(r"\[channel\]", f"{str(channel)}", output)

                        server_data["sent_hall_messages"].remove(sent_message)
                        await message.channel.send(output)
                        await hall_message.delete()
                        return oap.log(text=f"A message got removed from the hall of {hall}", cog="Events", color="magenta")


    # ==================================================
    # On reaction add event
    # ==================================================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction_event(payload)

    # ==================================================
    # On reaction remove event
    # ==================================================
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self.reaction_event(payload)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Events", color="magenta")
    bot.add_cog(Events(bot))
    reload(oap)
