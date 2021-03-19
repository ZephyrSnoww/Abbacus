from PIL import ImageFont, Image, ImageDraw
from urllib.request import urlopen, Request
import ovalia_auxiliary_protocol as oap
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from importlib import reload
import discord
import random
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
    @commands.command(brief="Test a color by hexadecimal value", help="", usage="[color] [True/False for transparency]")
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
        # Get rid of hashtag if the color starts with it
        # Check if color is a valid hex code
        # ==================================================
        if color.startswith("#"):
            color = color[1:]
        if len(color) != 6:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid hex value", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Variable definitions
        # Make the image background transparent if specified
        # Load the authors avatar
        # Load two sizes of font
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
        # Two colors lighter by 60/120
        # Two colors darker by 60/120
        # ==================================================
        lighter = [(i + 120) if (i + 120) < 255 else 255 for i in color]
        light = [(i + 60) if (i + 60) < 255 else 255 for i in color]
        dark = [(i - 60) if (i - 60) > 0 else 0 for i in color]
        darker = [(i - 120) if (i - 120) > 0 else 0 for i in color]

        # ==================================================
        # Draw everything on the image
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
        # Add the authors avatar
        # Save the image
        # ==================================================
        draw.rectangle([6, 115-34, 6+32, 115-2], fill=tuple(darker))
        img.paste(avatar, (0+4, 115-36))
        img.save("images/colors/test.png")

        # ==================================================
        # Send the image and log to console
        # ==================================================
        await ctx.send(file=discord.File("images/colors/test.png"))
        oap.log(text=f"Tested color #{old_color}", cog="Images", color="red", ctx=ctx)


    # ==================================================
    # Alter command
    # ==================================================
    @commands.command(brief="See what youd look like if you were a little different", usage="[pfp, name, or color] [name or color hex] <message>", help="")
    async def alter(self, ctx, what="", to="", *, message=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Argument checking
        # ==================================================
        if what == "":
            embed = oap.makeEmbed(title="Whoops!", description="Please enter something to change\nValid options are pfp (profile picture), name, or color", ctx=ctx)
            return await ctx.send(embed=embed)
        
        if what not in ["pfp", "name", "color", "none"]:
            embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid option\nValid options are pfp (profile picture), name, or color", ctx=ctx)
            return await ctx.send(embed=embed)

        if to == "" and what != "pfp":
            embed = oap.makeEmbed(title="Whoops!", description=f"Please enter {'a valid hex code' if what == 'color' else 'a name'}", ctx=ctx)
            return await ctx.send(embed=embed)

        # ==================================================
        # Grabbing variables
        # ==================================================
        user_name = to if (what == "name") else (ctx.author.name if ctx.author.nick == None else ctx.author.nick)
        user_color = ctx.author.color.to_rgb() if ctx.author.color.to_rgb() != (0, 0, 0) else (255, 255, 255)

        if what == "pfp":
            if len(ctx.message.attachments) == 0:
                embed = oap.makeEmbed(title="Whoops!", description="Please attach an image for me to use", ctx=ctx)
                return await ctx.send(embed=embed)
            
            avatar_req = Request(ctx.message.attachments[0].url, headers={"User-Agent": "Mozilla/5.0"})
            resize = True
        else:
            avatar_req = Request(str(ctx.author.avatar_url_as(static_format="png", size=64)), headers={"User-Agent": "Mozilla/5.0"})
            resize = False

        user_avatar = Image.open(urlopen(avatar_req))
        if resize:
            user_avatar = user_avatar.resize((64, 64))

        # ==================================================
        # Round the users avatar
        # ==================================================
        background_color = Image.new(user_avatar.mode, user_avatar.size, (54, 57, 62))
        mask = Image.new("L", user_avatar.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, user_avatar.size[0], user_avatar.size[1]), fill=255)
        
        user_avatar = Image.composite(user_avatar, background_color, mask)

        # ==================================================
        # If they didnt alter anything
        # Just send it
        # ==================================================
        # if what == "none" and to == "none":
            

        # ==================================================
        # If theyre changing the color
        # Get rid of hashtag if the color starts with it
        # Check if color is a valid hex code
        # ==================================================
        if what == "color":
            if to.startswith("#"):
                to = to[1:]
            if len(to) != 6:
                embed = oap.makeEmbed(title="Whoops!", description="Please enter a valid hex value", ctx=ctx)
                return await ctx.send(embed=embed)
            
            user_color = oap.hexToRGB(to)

        # ==================================================
        # Make the base image
        # ==================================================

        font1 = ImageFont.truetype("fonts/Helvetica-Bold.ttf", 26)
        font2 = ImageFont.truetype("fonts/Helvetica.ttf", 24)
        font3 = ImageFont.truetype("fonts/Helvetica.ttf", 18)
        temp_output = Image.new("RGB", (600, 80), (54, 57, 62))
        draw = ImageDraw.Draw(temp_output)
        output = Image.new("RGB", (600 if (draw.textsize("This is the default test message" if message == "" else message, font=font2)[0] + 30 + 64) < 600 else (draw.textsize("This is the default test message" if message == "" else message, font=font2)[0] + 30 + 64), 80), (54, 57, 62))
        output.paste(user_avatar, (10, 10))
        draw = ImageDraw.Draw(output)
        draw.text((89, 10), user_name, user_color, font=font1)
        draw.text((89, 45), "This is the default test message" if message == "" else message, font=font2)
        draw.text((99+draw.textsize(user_name, font=font1)[0], 18), f"Today at {(datetime.now()).strftime('%I:%M %p')}", (112, 118, 125), font=font3)
    
        # ==================================================
        # Save image
        # ==================================================
        output.save(("images/alter.png"))

        # ==================================================
        # Send output
        # Log to console
        # ==================================================
        await ctx.send(file=discord.File("images/alter.png"))
        oap.log(text="Altered themself", cog="Images", color="red", ctx=ctx)


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
        # If they didnt supply an image, use their pfp
        # If they gave an amount above or below the max/min, cap it
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
        # Get the attached image from url
        # Scale it down based on what they supplied
        # Scale it back up using nearest neighbor aliasing
        # Save it
        # ==================================================
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(urlopen(req))
        w, h = img.size
        img = img.resize((math.ceil(w/amount), math.ceil(h/amount)))
        img = img.resize((w, h), Image.NEAREST)
        img.save("images/pixelated.png")
    
        # ==================================================
        # Send the image and log to console
        # ==================================================
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
        # If they didnt supply an image, use their pfp
        # If they supplied an amount above or below the max/min, cap it
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
        # Get the attached image from url
        # Scale it down based on how much they supplied
        # Scale it back up with nearest neighbor aliasing
        # Save it with compression
        # ==================================================
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(urlopen(req))
        w, h = img.size
        img = img.resize((math.ceil(w/pixelation_amount), math.ceil(h/pixelation_amount)))
        img = img.resize((w, h), Image.NEAREST)
        img = img.convert("RGB")
        img.save("images/destroyed.jpg", quality=10-compression_amount)
    
        # ==================================================
        # Send the image and log to console
        # ==================================================
        await ctx.send(file=discord.File("images/destroyed.jpg"))
        oap.log(text="Destroyed an image", cog="Images", color="red", ctx=ctx)


    # ==================================================
    # Caption command
    # ==================================================
    @commands.command(brief="Caption an image", usage="bottom=\"\" and/or top=\"\"", help="")
    async def caption(self, ctx, *, text=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Arg checking
        # If they didnt supply an image, use their pfp
        # ==================================================
        if text == "":
            embed = oap.makeEmbed(title="Whoops!", description="Please enter some text", ctx=ctx)
            return await ctx.send(embed=embed)

        if len(ctx.message.attachments) == 0:
            url = str(ctx.author.avatar_url_as(static_format="png", size=256))
        else:
            url = ctx.message.attachments[0].url

        # ==================================================
        # Get variables from arguments
        # ==================================================
        top_text = re.findall(r'top="([^"]+)"', text)[0] if len(re.findall(r'top="([^"]+)"', text)) != 0 else ""
        bottom_text = re.findall(r'bottom="([^"]+)"', text)[0] if len(re.findall(r'bottom="([^"]+)"', text)) != 0 else ""
        base_font_size = int(re.findall(r'size=(\d+)', text)[0]) if len(re.findall(r'size=(\d+)', text)) != 0 else 12

        # ==================================================
        # Get the image from the url
        # Load the font
        # Load the image for drawing
        # Get how big the text will be for centering
        # ==================================================
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(urlopen(req))
        font_size = (base_font_size*math.floor(img.width/100))
        font = ImageFont.truetype("fonts/impact.ttf", font_size)
        draw = ImageDraw.Draw(img)
        text1w, text1h = draw.textsize(top_text, font)
        text2w, text2h = draw.textsize(bottom_text, font)

        # ==================================================
        # Caption and save the image
        # ==================================================
        draw.text((img.width/2 - text1w/2, (math.floor(img.width/100))), top_text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)
        draw.text((img.width/2 - text2w/2, img.height-((5*math.floor(img.width/100))+font_size)), bottom_text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)

        img.save("images/captioned.png")
    
        # ==================================================
        # Send the image and log to console
        # ==================================================
        await ctx.send(file=discord.File("images/captioned.png"))
        oap.log(text=f"Captioned an image", cog="Images", color="red", ctx=ctx)


    # ==================================================
    # Broken Caption command
    # ==================================================
    @commands.command(brief="Caption an image. a lot", usage="tops=[string 1, string 2, string 3] bottoms=[string 1, string 2, string 3]", help="")
    async def broken_caption(self, ctx, *, text=""):
        server_data = oap.getJson(f"servers/{ctx.guild.id}")
        if server_data.get("delete_invocation") == True:
            await oap.tryDelete(ctx)
    
        # ==================================================
        # Arg checking
        # If they didnt supply an image, use their pfp
        # ==================================================
        if text == "":
            embed = oap.makeEmbed(title="Whoops!", description="Please enter some text", ctx=ctx)
            return await ctx.send(embed=embed)

        if len(ctx.message.attachments) == 0:
            url = str(ctx.author.avatar_url_as(static_format="png", size=256))
        else:
            url = ctx.message.attachments[0].url

        # ==================================================
        # Get variables from arguments
        # ==================================================
        top_texts = re.findall(r'tops=\[(([^\[\]]+(, )*)+)\]', text)[0][0] if len(re.findall(r'tops=\[(([^\[\]]+(, )*)+)\]', text)) != 0 else ""
        bottom_texts = re.findall(r'bottoms=\[(([^\[\]]+(, )*)+)\]', text)[0][0] if len(re.findall(r'bottoms=\[(([^\[\]]+(, )*)+)\]', text)) != 0 else ""
        # top_text = re.findall(r'top="([^"]+)"', text)[0] if len(re.findall(r'top="([^"]+)"', text)) != 0 else ""
        # bottom_text = re.findall(r'bottom="([^"]+)"', text)[0] if len(re.findall(r'bottom="([^"]+)"', text)) != 0 else ""
        # base_font_size = int(re.findall(r'size=(\d+)', text)[0]) if len(re.findall(r'size=(\d+)', text)) != 0 else 12\

        top_texts = top_texts.split(", ")
        bottom_texts = bottom_texts.split(", ")

        # ==================================================
        # Get the image from the url
        # Load the font
        # Load the image for drawing
        # Get how big the text will be for centering
        # ==================================================
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        img = Image.open(urlopen(req))

        for text in top_texts:
            font_size = (random.randint(4, 18)*math.floor(img.width/100))
            font = ImageFont.truetype("fonts/impact.ttf", font_size)
            draw = ImageDraw.Draw(img)
            text1w, text1h = draw.textsize(text, font)
            # text2w, text2h = draw.textsize(bottom_text, font)

            # ==================================================
            # Caption and save the image
            # ==================================================
            draw.text((img.width/2 - text1w/2, (math.floor(img.width/100))), text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)
            # draw.text((img.width/2 - text2w/2, img.height-((5*math.floor(img.width/100))+font_size)), bottom_text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)

        for text in bottom_texts:
            font_size = (random.randint(4, 18)*math.floor(img.width/100))
            font = ImageFont.truetype("fonts/impact.ttf", font_size)
            draw = ImageDraw.Draw(img)
            text1w, text1h = draw.textsize(text, font)
            # text2w, text2h = draw.textsize(bottom_text, font)

            # ==================================================
            # Caption and save the image
            # ==================================================
            # draw.text((img.width/2 - text1w/2, (math.floor(img.width/100))), text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)
            draw.text((img.width/2 - text1w/2, img.height-((5*math.floor(img.width/100))+font_size)), text, stroke_width=math.floor(img.width/100), stroke_fill=(0, 0, 0), font=font)

        img.save("images/captioned.png")
    
        # ==================================================
        # Send the image and log to console
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
