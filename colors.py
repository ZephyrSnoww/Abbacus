from PIL import ImageFont, Image, ImageDraw
import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from urllib.request import urlopen, Request
from importlib import reload
import discord


class Colors(commands.Cog, description="Color generation and image manipulation"):
    def __init__(self, bot):
        self.abacus = bot
        self.data = oap.getJson("data")

    # ==================================================
    # Unload event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="Colors", color="red")


    # ==================================================
    # Testcolor command
    # ==================================================
    @commands.command(brief="Test a color by hexadecimal value", help="")
    async def testcolor(self, ctx, color=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        if color == "":
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a color", ctx=ctx)
            return await ctx.send(embed=embed)
        
        if color.startswith("#"):
            color = color[1:]
        if len(color) != 6:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid hex value", ctx=ctx)
            return await ctx.send(embed=embed)

        old_color = f"{color}"
        color = oap.hexToRGB(color)
        img = Image.new("RGB", (200, 115), color=color)
        req = Request(str(ctx.author.avatar_url_as(static_format="png", size=32)), headers={"User-Agent": "Mozilla/5.0"})
        avatar = Image.open(urlopen(req))
        draw = ImageDraw.Draw(img)

        lighter = [(i + 120) if (i + 120) < 255 else 255 for i in color]
        light = [(i + 60) if (i + 60) < 255 else 255 for i in color]
        dark = [(i - 60) if (i - 60) > 0 else 0 for i in color]
        darker = [(i - 120) if (i - 120) > 0 else 0 for i in color]

        draw.text((7, 4), ("#%s" % old_color).upper(), tuple(darker))
        draw.text((5, 2), ("#%s" % old_color).upper(), (255, 255, 255))
        draw.text((150, 6), ("#%02x%02x%02x" % tuple(lighter)).upper(), tuple(lighter))
        draw.text((150, 6), ("\n#%02x%02x%02x" % tuple(light)).upper(), tuple(light))
        draw.text((150, 6), ("\n\n#%02x%02x%02x" % tuple(dark)).upper(), tuple(dark))
        draw.text((150, 2), ("\n\n\n#%02x%02x%02x" % tuple(darker)).upper(), tuple(darker))

        img.paste(avatar, (0+4, 115-36))
        img.save("images/colors/test.png")

        await ctx.send(file=discord.File("images/colors/test.png"))
        oap.log(text=f"Tested color #{old_color}", cog="Colors", color="red", ctx=ctx)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Colors", color="red")
    bot.add_cog(Colors(bot))
    reload(oap)
