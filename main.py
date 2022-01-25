import discord
from discord.ext import commands
import requests
import asyncio
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

bot = commands.Bot(command_prefix="$")

TOKEN = os.getenv('TOKEN')
MESSAGE_ID = int(os.getenv('MESSAGE_ID'))
RESUME_CHANNEL = int(os.getenv('RESUME_CHANNEL'))
SUBMISSION_CHANNEL = int(os.getenv('SUBMISSION_CHANNEL'))


async def ctx_input(ctx, bot, timeout=60.0):
    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.member
        )
        if msg:
            _id = msg.content
            await msg.delete()
            return _id
    except asyncio.TimeoutError as err:
        await ctx.send('Cancelling due to timeout.', delete_after=timeout)
        return None


async def ctx_upload(ctx, bot, timeout=60.0):
    def check(message):
        return message.author == ctx.member and bool(message.attachments)

    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=check
        )
        if msg:
            await msg.delete()
            return msg
    except asyncio.TimeoutError as err:
        await ctx.send('Cancelling due to timeout.', delete_after=timeout)
        return None


@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != '✅':
        return

    user = payload.member
    if user.bot is True or payload.message_id != MESSAGE_ID:
        return

    ctx = bot.get_channel(SUBMISSION_CHANNEL)
    try:
        await ctx.send("Enter your name", delete_after=10.0)
        name = await ctx_input(payload, bot)

        await ctx.send("Enter your email", delete_after=10.0)
        email = await ctx_input(payload, bot)

        await ctx.send("Enter your phone", delete_after=10.0)
        phone = await ctx_input(payload, bot)

        await ctx.send("Upload your resume", delete_after=10.0)
        ctx = await ctx_upload(payload, bot)

        for attachment in ctx.attachments:
            if attachment.url.endswith(".pdf"):
                filename = name + "-" + phone + "-" + email + ".pdf"
                create_pdf_file(attachment.url, filename)
                channel = bot.get_channel(RESUME_CHANNEL)
                await channel.send(file=discord.File(filename))

    except Exception:
        channel = bot.get_channel(RESUME_CHANNEL)
        await channel.send("Something went wrong. Please try again.", delete_after=5.0)
        return


def create_pdf_file(url, filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)


bot.run(TOKEN)
