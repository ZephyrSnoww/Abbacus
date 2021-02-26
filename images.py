from PIL import ImageFont, Image, ImageDraw
import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from urllib.request import urlopen, Request
from importlib import reload
import discord
import math
import re


class Images(commands.Cog, description="Color generation and image manipulation"):
    def __init__(self, bot):
        self.abacus = bot
        self.data = oap.getJson("data")

    # ==================================================
    # Unload event
    # ==================================================
    def cog_unload(self):
        oap.log(text="Unloaded", cog="Images", color="red")


    # ==================================================
    # Testcolor command
    # ==================================================
    @commands.command(brief="Test a color by hexadecimal value", help="")
    async def testcolor(self, ctx, color="", transparent=False):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # Arg checking
        # ==================================================
        if color == "":
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a color", ctx=ctx)
            return await ctx.send(embed=embed)
        
        # ==================================================
        # Get rid of hashtag if it starts with it
        # Check if color is a valid hex code
        # ==================================================
        if color.startswith("#"):
            color = color[1:]
        if len(color) != 6:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid hex value", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Variable definitions
        # ==================================================
        old_color = f"{color}"
        color = oap.hexToRGB(color)
        if not transparent:
            img = Image.new("RGB", (235, 115), color=color)
        else:
            img = Image.new("RGBA", (235, 115), color=(0, 0, 0, 0))
        req = Request(str(ctx.author.avatar_url_as(static_format="png", size=32)), headers={"User-Agent": "Mozilla/5.0"})
        avatar = Image.open(urlopen(req))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("fonts/fredokaone.ttf", 24)
        font2 = ImageFont.truetype("fonts/fredokaone.ttf", 18)

        # ==================================================
        # Making the lighter and darker colors
        # ==================================================
        lighter = [(i + 120) if (i + 120) < 255 else 255 for i in color]
        light = [(i + 60) if (i + 60) < 255 else 255 for i in color]
        dark = [(i - 60) if (i - 60) > 0 else 0 for i in color]
        darker = [(i - 120) if (i - 120) > 0 else 0 for i in color]

        # ==================================================
        # Drawing everything on the image
        # ==================================================
        draw.text((7, 4), ("#%s" % old_color).upper(), tuple(darker), font=font)
        draw.text((5, 2), ("#%s" % old_color).upper(), ((255, 255, 255) if not transparent else color), font=font)
        draw.text((150, 4), ("#%02x%02x%02x" % tuple(lighter)).upper(), tuple(lighter), font=font2)
        draw.text((150, 4), ("\n#%02x%02x%02x" % tuple(light)).upper(), tuple(light), font=font2)
        draw.text((150, 4), ("\n\n#%02x%02x%02x" % tuple(dark)).upper(), tuple(dark), font=font2)
        draw.text((150, 2), ("\n\n\n#%02x%02x%02x" % tuple(darker)).upper(), tuple(darker), font=font2)

        draw.text((43, 115-21), ctx.author.nick if ctx.author.nick else ctx.author.name, tuple(darker), font=font2)
        draw.text((41, 115-23), ctx.author.nick if ctx.author.nick else ctx.author.name, ((255, 255, 255) if not transparent else color), font=font2)

        # ==================================================
        # Adding the authors avatar
        # ==================================================
        draw.rectangle([6, 115-34, 6+32, 115-2], fill=tuple(darker))
        img.paste(avatar, (0+4, 115-36))
        img.save("images/colors/test.png")

        # ==================================================
        # Output
        # ==================================================
        await ctx.send(file=discord.File("images/colors/test.png"))
        oap.log(text=f"Tested color #{old_color}", cog="Images", color="red", ctx=ctx)


    # ==================================================
    # Pixelate command
    # ==================================================
    @commands.command(brief="Pixelate an image", usage="[amount]", help="Pixelate an image with a specified amount.\nAmount ranges from 1-100")
    async def pixelate(self, ctx, amount=20):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # Arg checking
        # ==================================================
        if len(ctx.message.attachments) == 0:
            url = str(ctx.author.avatar_url_as(static_format="png", size=256))
        else:
            url = ctx.message.attachments[0].url

        if amount < 1:
            amount = 1
        if amount > 100:
            amount = 100
    
        # ==================================================
        # Get the attached image and scale it
        # ==================================================
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(urlopen(req))
        w, h = img.size
        img = img.resize((math.ceil(w/amount), math.ceil(h/amount)))
        img = img.resize((w, h), Image.NEAREST)
        img.save("images/pixelated.png")
    
        await ctx.send(file=discord.File("images/pixelated.png"))
        oap.log(text="Pixelated an image", cog="Images", color="red", ctx=ctx)

    
    # ==================================================
    # Destroy command
    # ==================================================
    @commands.command(brief="Add some jpeg compression", usage="[pixelation_amount] [compression_amount]", help="Add jpeg compression to an image, with a specified amount.\nPixelation amount ranges from 1-100\nCompression amount ranges from 1-10")
    async def destroy(self, ctx, pixelation_amount=10, compression_amount=1):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)

        # ==================================================
        # Arg checking
        # ==================================================
        if len(ctx.message.attachments) == 0:
            url = str(ctx.author.avatar_url_as(static_format="png", size=256))
        else:
            url = ctx.message.attachments[0].url

        if pixelation_amount < 1:
            pixelation_amount = 1
        if pixelation_amount > 100:
            pixelation_amount = 100
        if compression_amount > 5:
            amount = 5
        if compression_amount < 1:
            amount = 1
    
        # ==================================================
        # Get the attached image and scale it
        # ==================================================
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(urlopen(req))
        w, h = img.size
        img = img.resize((math.ceil(w/pixelation_amount), math.ceil(h/pixelation_amount)))
        img = img.resize((w, h), Image.NEAREST)
        img = img.convert("RGB")
        img.save("images/destroyed.jpg", quality=10-compression_amount)
    
        await ctx.send(file=discord.File("images/destroyed.jpg"))
        oap.log(text="Destroyed an image", cog="Images", color="red", ctx=ctx)


    # ==================================================
    # Caption command
    # ==================================================
    @commands.command(brief="", usage="", help="")
    async def caption(self, ctx, *, text=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Arg checking
        # ==================================================
        if text == "":
            embed = oap.makeEmbed(title="Whoops!", description="Please enter some text", ctx=ctx)
            return await ctx.send(embed=embed)

        if len(ctx.message.attachments) == 0:
            url = str(ctx.author.avatar_url_as(static_format="png", size=256))
        else:
            url = ctx.message.attachments[0].url

        # ==================================================
        # Get variables
        # ==================================================
        top_text = re.findall(r'top="([^"]+)"', text)[0] if len(re.findall(r'top="([^"]+)"', text)) != 0 else ""
        bottom_text = re.findall(r'bottom="([^"]+)"', text)[0] if len(re.findall(r'bottom="([^"]+)"', text)) != 0 else ""

        # ==================================================
        # Get the image and all variables
        # ==================================================
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(urlopen(req))
        font_size = (12*math.floor(img.width/100))
        font = ImageFont.truetype("fonts/impact.ttf", font_size)
        draw = ImageDraw.Draw(img)
        text1w, text1h = draw.textsize(top_text, font)
        text2w, text2h = draw.textsize(bottom_text, font)

        # ==================================================
        # Caption the image
        # ==================================================
        draw.text((img.width/2 - text1w/2, (math.floor(img.width/100))), top_text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)
        draw.text((img.width/2 - text2w/2, img.height-((5*math.floor(img.width/100))+font_size)), bottom_text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)

        img.save("images/captioned.png")
    
        # ==================================================
        # Output
        # ==================================================
        await ctx.send(file=discord.File("images/captioned.png"))
        oap.log(text=f"Captioned an image", cog="Images", color="red", ctx=ctx)


# ==================================================
# Cog setup
# ==================================================
def setup(bot):
    oap.log(text="Loaded", cog="Images", color="red")
    bot.add_cog(Images(bot))
    reload(oap)
