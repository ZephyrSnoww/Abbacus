import ovalia_auxiliary_protocol as oap
from discord.ext import commands
from importlib import reload
from aiohttp import web
from os import listdir
import requests
import asyncio
import discord
import inspect
import json
import re


class Webserver(commands.Cog, description="Interfacing with an online control panel"):
    def __init__(self, bot):
        self.abacus = bot
        self.cog_name = "Webserver"
        self.data = oap.getJson("data")

    # ==================================================
    # Unload Event
    # ==================================================
    def cog_unload(self):
        asyncio.ensure_future(self.site.stop())
        oap.log(text="Unloaded", cog=self.cog_name)


    # ==================================================
    # The webserver
    # ==================================================
    async def webserver(self):
        # ==================================================
        # Basic request
        # Returns html of page
        # ==================================================
        async def handler(request):
            return web.FileResponse("./webserver-html")

        # ==================================================
        # User settings tab request
        # Returns the page html with user settings selected
        # ==================================================
        async def user_settings(request):
            with open("./webserver.html", "r") as htmlFile:
                content = re.sub(r"#info-container", "#user-settings-container1", htmlFile.read())
                content = re.sub(r"#user-settings-container(?!\d)", "#info-container", content)
                content = re.sub(r"#user-settings-container1", "#user-settings-container", content)
                return web.Response(text=content, content_type='text/html')

        # ==================================================
        # Server settings tab request
        # Returns the page html with server settings selected
        # ==================================================
        async def server_settings(request):
            with open("./webserver.html", "r") as htmlFile:
                content = re.sub(r"#info-container", "#server-settings-container1", htmlFile.read())
                content = re.sub(r"#server-settings-container(?!\d)", "#info-container", content)
                content = re.sub(r"#server-settings-container1", "#server-settings-container", content)
                return web.Response(text=content, content_type='text/html')

        # ==================================================
        # User token request
        # Gets a users data and id
        # Returns them to client
        # ==================================================
        async def user_token(request):
            token = str(request.url).split("=")[1]
            # print(token)

            r = requests.get(f"https://discord.com/api/oauth2/@me", headers={"Authorization": "Bearer " + token})
            data = r.json()

            id = data["user"]["id"]

            userdata = oap.getJson(f"users/{id}")
            if userdata == {}:
                userdata = {
                    "color": 0xffadb6
                }

            userdata["id"] = id

            return web.json_response(userdata)

        # ==================================================
        # Set user settings request
        # Writes given user data to a json file
        # Returns confirmation
        # ==================================================
        async def set_user_settings(request):
            query = request.rel_url.query
            id = query["id"]
            color = query["color"]

            userdata = oap.getJson(f"users/{id}")

            userdata["color"] = int(color, 16)

            oap.setJson(f"users/{id}", userdata)

            return web.Response(text="aight")

        async def set_server_settings(request):
            query = request.rel_url.query
            user_id = query["user-id"]
            server_id = query["server-id"]
            json_data = await request.json()

            guild = self.abacus.get_guild(int(server_id))
            channels = [[channel.id, channel.name] for channel in guild.text_channels]

            server_data = oap.getJson(f"servers/{server_id}")

            # ==================================================
            # Setting hall data
            # ==================================================
            for key, value in json_data["halls"].items():
                if server_data["halls"].get(key) != None:
                    server_data["halls"][key]["requirement"] = value["requirement"]
                    server_data["halls"][key]["announcement message"] = value["announcement"]
                    server_data["halls"][key]["announcement message enabled"] = value["announcement enabled"]
                    server_data["halls"][key]["removal message"] = value["removal"]
                    server_data["halls"][key]["removal message enabled"] = value["removal enabled"]
                    server_data["halls"][key]["placement message"] = value["placement"]
                    server_data["halls"][key]["placement message proxied"] = value["placement proxied"]

                    for channel in channels:
                        if value["channel"] == channel[1]:
                            server_data["halls"][key]["channel"] = f"<#{channel[0]}>"
                    
                    if key != value["name"]:
                        server_data["halls"][value["name"]] = server_data["halls"].pop(key)
                        for _name, _hall in server_data["halls"].items():
                            if _hall["rival hall"] == key:
                                server_data["halls"][_name]["rival hall"] = value["name"]

            oap.setJson(f"servers/{server_id}", server_data)

            return web.Response(text="aight")

        async def set_hall_emoji(request):
            query = request.rel_url.query
            user_id = query["user-id"]
            server_id = query["server-id"]
            json_data = await request.json()
            hall_name = json_data["hall name"]
            server_data = oap.getJson(f"servers/{server_id}")

            guild = self.abacus.get_guild(int(server_id))
            user = await guild.fetch_member(int(user_id))

            def check(message):
                return message.author.id == int(user_id)

            await user.send(embed=oap.makeEmbed(
                title=f"Setting {hall_name} Emoji",
                description=f"Please send the emoji you would like to use for the {hall_name} hall!",
            ))

            emoji_message = await self.abacus.wait_for("message", check=check)

            hall_emoji = emoji_message.content.split(" ")[0]
            invalid_emoji = True

            # ==================================================
            # While the emoji is invalid
            # ==================================================
            while invalid_emoji:
                # ==================================================
                # Check if they want to cancel creation
                # ==================================================
                if emoji_message.content == "cancel":
                    await user.send(embed=oap.makeEmbed(
                        embed_title=f"Alright!",
                        embed_description=f"Hall editing cancelled!",
                    ))
                    return web.json_response({
                        "type": "cancel"
                    })

                # ==================================================
                # Try to add the emoji as a reaction
                # (Test if the emoji is valid)
                # ==================================================
                try:
                    await emoji_message.add_reaction(hall_emoji)
                    await emoji_message.remove_reaction(hall_emoji, self.abacus.user)
                    invalid_emoji = False

                # ==================================================
                # If not valid
                # Ask for a new emoji
                # ==================================================
                except:
                    embed = oap.makeEmbed(
                        title=f"Whoops!",
                        description=f"""\
                            "{emoji_message.content}" isn't a valid emoji.

                            Try again, or cancel editing with "cancel"!
                        """
                    )

                    # ==================================================
                    # Send output and wait for message back
                    # ==================================================
                    await user.send(embed=embed)
                    emoji_message = await self.abacus.wait_for("message", check=check)
                    hall_emoji = emoji_message.content.split(" ")[0]

            server_data["halls"][hall_name]["emoji"] = hall_emoji

            oap.setJson(f"servers/{server_id}", server_data)
            
            await user.send(embed=oap.makeEmbed(
                embed_title=f"Alright!",
                embed_description=f"Changed hall emoji!",
            ))

            return web.json_response({
                "type": "success"
            })

        # ==================================================
        # Returns the favicon
        # ==================================================
        async def favicon(request):
            return web.FileResponse("./favicon.ico")

        # ==================================================
        # Fetch servers request
        # Returns all servers the client has the manage guild permission in
        # ==================================================
        async def fetch_servers(request):
            query = request.rel_url.query
            id = query.get("id")

            valid_guilds = []

            for file in listdir("./servers/"):
                guild_id = file[:-5]
                try:
                    guild = self.abacus.get_guild(int(guild_id))
                except discord.errors.Forbidden:
                    continue
                if guild != None:
                    member = await guild.fetch_member(int(id))
                    if member:
                        if member.guild_permissions.manage_guild:
                            valid_guilds.append(guild.name)

            return web.json_response({
                "servers": valid_guilds
            })

        # ==================================================
        # Server data request
        # Returns a servers data
        # ==================================================
        async def fetch_server_data(request):
            query = request.rel_url.query
            server_name = query.get("server")

            server_data = {
                "error": "no server"
            }

            real_server_id = "";
            channels = []

            for file in listdir("./servers/"):
                server_id = file[:-5]
                try:
                    guild = self.abacus.get_guild(int(server_id))
                except discord.errors.Forbidden:
                    continue
                if guild != None:
                    if guild.name == server_name:
                        real_server_id = server_id
                        server_data = oap.getJson(f"servers/{server_id}")
                        for channel in guild.text_channels:
                            channels.append([channel.id, channel.name])

            if server_data.get("error") == None:
                server_data["server id"] = real_server_id
                server_data["channels"] = channels

            return web.json_response(server_data)

        # ==================================================
        # Making the app
        # ==================================================
        app = web.Application()
        app.router.add_route('GET', "/", handler)
        app.router.add_route('GET', "/user-settings", user_settings)
        app.router.add_route('GET', "/server-settings", server_settings)
        app.router.add_route('GET', "/user-token={tail:.+}", user_token)
        app.router.add_route('GET', "/set-user-settings", set_user_settings)
        app.router.add_route('POST', "/set-server-settings", set_server_settings)
        app.router.add_route('POST', "/set-hall-emoji", set_hall_emoji)
        app.router.add_route('GET', "/favicon.ico", favicon)
        app.router.add_route('GET', "/fetch-servers", fetch_servers)
        app.router.add_route('GET', "/fetch-server-data", fetch_server_data)
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, 'localhost', 2418)
        await self.abacus.wait_until_ready()
        await self.site.start()







    # ==================================================
    # WEBSERVER REMAKE 
    # ==================================================
    async def webserver_remake(self):
        # ==================================================
        # Basic response, returns webpage
        # Return stylesheet
        # Return javascript
        # ==================================================
        async def getIndex(request):
            return web.FileResponse("./webserver_remake_2.html")

        async def getStyleSheet(request):
            return web.FileResponse("./webserver_stylesheet_2.css")

        async def getJavascript(request):
            return web.FileResponse("./webserver_javascript_2.js")

        async def getIcon(request):
            return web.FileResponse("./icon.jpg")
        
        async def getFavicon(request):
            return web.FileResponse("./favicon.ico")
        
        async def getWave(request):
            return web.FileResponse("./wave.png")
        
        async def getBackground(request):
            return web.FileResponse("./background.png")


        # ==================================================
        # User settings request
        # Returns user data and id
        # ==================================================
        async def getUserData(request):
            request_json = await request.json()

            # ==================================================
            # Request their user info
            # ==================================================
            r = requests.get(f"https://discord.com/api/oauth2/@me", headers={"Authorization": "Bearer " + request_json['bearer_token']})
            request_data = r.json()

            user_id = request_data["user"]["id"]

            # ==================================================
            # Get their user data
            # ==================================================
            user_data = oap.getJson(f"users/{user_id}")

            # ==================================================
            # Check what guilds they can edit
            # ==================================================
            valid_servers = []

            for file in listdir("./servers/"):
                server_id = file[:-5]
                try:
                    server = self.abacus.get_guild(int(server_id))
                except discord.errors.Forbidden:
                    continue
                if server != None:
                    member = await server.fetch_member(int(user_id))
                    if member:
                        if member.guild_permissions.manage_guild:
                            valid_servers.append([server.name, server_id])

            # ==================================================
            # Set defaults if userdata not found
            # ==================================================
            if user_data == {}:
                user_data = {"color": 0xffadb6}

            # ==================================================
            # Add their id to the info
            # ==================================================
            user_data["id"] = user_id
            user_data["valid_servers"] = valid_servers

            # ==================================================
            # Send response
            # ==================================================
            return web.json_response(user_data)


        # ==================================================
        # Get server settings request
        # Returns server data and id
        # ==================================================
        async def getServerData(request):
            request_json = await request.json()

            # ==================================================
            # Go through all servers with settings
            # ==================================================
            for file in listdir("./servers/"):
                server_id = file[:-5]

                # ==================================================
                # Get the guild object
                # ==================================================
                guild = self.abacus.get_guild(int(server_id))

                # ==================================================
                # If we found a guild
                # And its the same guild the user is asking for
                # ==================================================
                if guild != None:
                    if server_id == request_json["server_id"]:
                        # ==================================================
                        # Organize server data and send it to the users
                        # ==================================================
                        server_data = oap.getJson(f"servers/{guild.id}")
                        channels = [{"channel_id": channel.id, "channel_name": channel.name} for channel in guild.text_channels]
                        server_data["server_id"] = guild.id
                        server_data["server_name"] = guild.name
                        server_data["channels"] = channels
                        return web.json_response(server_data)

            # ==================================================
            # Return an error
            # ==================================================
            return web.json_response({
                "error": "no server found"
            })

        
        # ==================================================
        # Set user settings request
        # Returns json with settings updated
        # ==================================================
        async def setUserData(request):
            request_json = await request.json()
            settings_changed = {}

            # ==================================================
            # Get user data
            # ==================================================
            user_data = oap.getJson(f"users/{request_json['user_id']}")

            # ==================================================
            # Change all settings given
            # ==================================================
            for key, value in request_json["settings"].items():
                if user_data[key] != request_json["settings"][key]:
                    user_data[key] = value
                    settings_changed[key] = value

            # ==================================================
            # Set user data
            # ==================================================
            oap.setJson(f"users/{request_json['user_id']}", user_data)

            # ==================================================
            # Send json response
            # ==================================================
            return web.json_response(settings_changed)

        
        # ==================================================
        # Set server settings request
        # Returns json with setting supdated
        # ==================================================
        async def setServerData(request):
            request_json = await request.json()
            settings_changed = {}

            # ==================================================
            # Get server data
            # ==================================================
            server_data = oap.getJson(f"servers/{request_json['server_id']}")

            # ==================================================
            # Change all settings given
            # ==================================================
            for key, value in request_json["settings"].items():
                if server_data[key] != request_json["settings"][key]:
                    server_data[key] = value
                    settings_changed[key] = value

            # ==================================================
            # Set user data
            # ==================================================
            oap.setJson(f"users/{request_json['user_id']}", server_data)

            # ==================================================
            # Send json response
            # ==================================================
            return web.json_response(settings_changed)


        # ==================================================
        # Making the app
        # ==================================================
        app = web.Application()
        app.router.add_route("GET", "/", getIndex)
        app.router.add_route("GET", "/webserver-stylesheet.css", getStyleSheet)
        app.router.add_route("GET", "/webserver-javascript.js", getJavascript)
        app.router.add_route("GET", "/icon.jpg", getIcon)
        app.router.add_route("GET", "/favicon.ico", getFavicon)
        app.router.add_route("GET", "/wave.png", getWave)
        app.router.add_route("GET", "/background.png", getBackground)
        app.router.add_route("POST", "/get-user-data", getUserData)
        app.router.add_route("POST", "/set-user-data", setUserData)
        app.router.add_route("POST", "/get-server-data", getServerData)
        app.router.add_route("POST", "/set-server-data", setServerData)

        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, "localhost", 2418)
        await self.abacus.wait_until_ready()
        await self.site.start()


def setup(bot):
    oap.log(text="Loaded", cog="Webserver")
    webserver = Webserver(bot)
    bot.add_cog(webserver)
    bot.loop.create_task(webserver.webserver_remake())
    reload(oap)