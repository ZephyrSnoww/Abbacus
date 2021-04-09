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
        user = await self.abacus.fetch_user(payload.user_id)
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        emoji = str(payload.emoji)

        # ==================================================
        # Check if data exists
        # If it doesnt, just fill defaults
        # ==================================================
        if not server_data.get("halls"):
            return

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
        elif message.author.bot:
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

        if message.channel.id == server_data["halls"][hall]["channel"]:
            return

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
        if abs(score) >= requirement:
            if not server_data.get("sent_hall_messages"):
                server_data["sent_hall_messages"] = []
            
            # ==================================================
            # Check if the message is already in a hall
            # If so, just update the score
            # ==================================================
            in_hall = False
            for i in range(len(server_data["sent_hall_messages"])):
                if server_data["sent_hall_messages"][i]["id"] == payload.message_id:
                    server_data["sent_hall_messages"][i]["score"] = score
                    oap.setJson(f"servers/{guild.id}", server_data)
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
                output = re.sub(r"\[attachments\]", "\n".join([(f"|| {attachment.url} ||" if "SPOILER_" in attachment.url else attachment.url) for attachment in message.attachments]), output)
                output = re.sub(r"\[channel\]", f"{str(channel)}", output)

                # ==================================================
                # Format the message to be sent in the hall
                # ==================================================
                output2 = server_data["halls"]["message"]
                output2 = re.sub(r"\[user\]", f"{message.author.name}", output2)
                output2 = re.sub(r"\[attachments\]", "\n".join([(f"|| {attachment.url} ||" if "SPOILER_" in attachment.url else attachment.url) for attachment in message.attachments]), output2)
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
                return oap.log(
                    text=f"Got a message to the hall of {hall}",
                    cog="Events",
                    color="magenta",
                    payload=True,
                    guild=guild,
                    author=user)

        # ==================================================
        # If the score doesnt meet the requirement
        # Check if the message is in a hall
        # If it is, remove it
        # Send output
        # ==================================================
        if abs(score) < requirement:
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
                        oap.setJson(f"servers/{guild.id}", server_data)
                        await message.channel.send(output)
                        await hall_message.delete()
                        return oap.log(
                            text=f"Removed a message from the hall of {hall}",
                            cog="Events",
                            color="magenta",
                            payload=True,
                            guild=guild,
                            author=user)


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
    # On message event
    # ==================================================
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if message.content.startswith(">>"): return

        # ==================================================
        # Get server data
        # If they have autoresponders enabled
        # ==================================================
        server_data = oap.getJson(f"servers/{message.guild.id}")
        if server_data.get("autoresponder") == True:
            if server_data.get("autoresponders"):
                # ==================================================
                # Go through all existing autoresponders
                # Check the type, look for a match
                # Respond if any match
                # ==================================================
                for autoresponder in server_data["autoresponders"]:
                    respond = False
                    if autoresponder["type"] == "word":
                        if len(re.findall(rf"\b{autoresponder['trigger'].lower()}\b", message.content.lower())) > 0:
                            respond = True

                    if autoresponder["type"] == "anywhere":
                        if len(re.findall(rf"{autoresponder['trigger'].lower()}", message.content.lower())) > 0:
                            respond = True

                    if autoresponder["type"] == "beginning":
                        if len(re.findall(rf"^{autoresponder['trigger'].lower()}", message.content.lower())) > 0:
                            respond = True
                        
                    if autoresponder["type"] == "end":
                        if len(re.findall(rf"{autoresponder['trigger'].lower()}(?=$)", message.content.lower())) > 0:
                            respond = True

                    if respond:
                        await message.channel.send(autoresponder["response"])
                        oap.log(text="Autoresponder triggered", cog="Events", color="magenta", ctx=message)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Events", color="magenta")
    bot.add_cog(Events(bot))
    reload(oap)
