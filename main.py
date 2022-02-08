from discord.ext import commands
import json
import discord
import os
from redminelib import Redmine
from redminelib.exceptions import ResourceAttrError
from discord.ext import tasks
import asyncio
import chat_exporter
import requests
import io


bot = commands.Bot(command_prefix="$")
TOKEN = os.getenv('TOKEN')

url = "https://www.kore.koders.in"
key = os.getenv('REDMINE_KEY')
redmine = Redmine(url, key=key)


def get_discord_id(user_id):
    user = redmine.user.get(user_id)
    return user.custom_fields[0].value


def get_open_issues():
    redmine_open_issues = redmine.issue.filter(status='open')
    return redmine_open_issues


def extract_fields(issue):
    watchers = []
    issue_id = issue.id
    issue_description = issue.subject
    try:
        assigned_to = get_discord_id(issue.assigned_to.id)
    except ResourceAttrError:
        assigned_to = None

    assigned_by = get_discord_id(issue.author.id)

    if issue.watchers:
        for watcher in issue.watchers:
            watchers.append(get_discord_id(watcher.id))
    return issue_id, issue_description, assigned_to, assigned_by, watchers


def create_html_file(url, filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)


def get_file_token(filename, key):
    with open(filename, 'rb') as f:
        data = f.read()
    filename = 'https://kore.koders.in/uploads.json?filename=' + str(filename)
    res = requests.post(url=filename,
                        data=data,
                        headers={
                            'Content-Type': 'application/octet-stream',
                            'X-Redmine-API-Key': key
                        })
    data = json.loads(res.text)
    token = (data['upload']['token'])
    return token


async def has_channel(channel_name):
    channels = bot.get_all_channels()
    await asyncio.sleep(5)  # FIXME => Not a proper method to wait for a request. Will have to look for alternatives
    for channel in channels:
        if str(channel).startswith(channel_name):
            return True
    return False


async def create_issue_embed(issue_id, issue_description, assigned_to, assigned_by, watchers):
    embed = discord.Embed(title=issue_id, url="https://kore.koders.in/issues/" + str(issue_id),
                          description=issue_description,
                          color=0x00c7fc)
    embed.set_author(name="Issue Details")
    assigned_to = await bot.fetch_user(assigned_to)
    embed.add_field(name="Accountable", value=assigned_to.name, inline=True)
    assigned_by = await bot.fetch_user(assigned_by)
    embed.add_field(name="Leader", value=assigned_by.name, inline=True)
    watcher_users = []
    if watchers:
        for watcher in watchers:
            result = await bot.fetch_user(watcher)
            watcher_users.append(result.name)
    embed.add_field(name="Watchers", value=str(watcher_users), inline=False)
    embed.set_footer(text="Created with ❤️ by Redmine")
    return embed


async def create_text_channel(issue_id, issue_description, assigned_to, assigned_by, watchers):
    server = bot.get_guild(927231626260406283)
    channel_name = "issue-" + str(issue_id) + "-" + str(issue_description)
    channel = await server.create_text_channel(channel_name)
    await channel.set_permissions(server.default_role, read_messages=False)

    if assigned_to:
        await channel.set_permissions(await bot.fetch_user(assigned_to), read_messages=True)
    await channel.set_permissions(await bot.fetch_user(assigned_by), read_messages=True)
    for watcher in watchers:
        if watcher:
            await channel.set_permissions(await bot.fetch_user(watcher), read_messages=True)
    await channel.send(embed=await create_issue_embed(issue_id, issue_description, assigned_to, assigned_by, watchers))


async def remove_closed_channels():
    channels = bot.get_all_channels()
    await asyncio.sleep(5)  # FIXME => Not a proper method to wait for a request. Will have to look for alternatives
    for channel in channels:
        if str(channel.name).startswith('issue'):
            issue_id = channel.name.split('-')[1]
            # issue_id = channel.name.strip("issue-")
            issue = redmine.issue.get(issue_id)
            if str(issue.status) == 'Closed' or str(issue.status) == 'On Hold':
                archive_channel = bot.get_channel(id=938461049617809438)
                if channel and archive_channel:
                    transcript = await chat_exporter.export(channel, set_timezone='UTC')
                    transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"{issue_id}.html")
                    message = await archive_channel.send(file=transcript_file)

                    filename = str(issue_id) + '.html'
                    create_html_file(message.attachments[0].url, filename)
                    token = get_file_token(filename, key)
                    redmine.issue.update(
                        int(issue_id),
                        uploads=[{'token': token}]
                    )
                    await channel.delete()


async def delete_text_channel():  # Optional function for removing channels
    channels = bot.get_all_channels()
    await asyncio.sleep(5)  # fixme => not a proper method to wait for a request. will have to look for alternatives
    for channel in channels:
        if str(channel.category) == 'issues':
            await channel.delete()
    return False  # #


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send("*Private messages.* ", delete_after=60)
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send("*~Not have enough permission.*", delete_after=60)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("*Command is missing an argument:* ", delete_after=60)
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("*This command is currenlty disabled. Please try again later.* ", delete_after=60)
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("*You do not have the permissions to do this.* ", delete_after=60)


@tasks.loop(minutes=30)  # repeat after every 30 minutes
async def check_for_new_issues():
    # await delete_text_channel()
    issues = get_open_issues()
    for issue in issues:
        result = await has_channel("issue-" + str(issue.id))
        if not result:
            try:
                issue_id, issue_description, assigned_to, assigned_by, watchers = extract_fields(issue)
                await create_text_channel(issue_id, issue_description, assigned_to, assigned_by, watchers)
            except Exception as e:
                print('something went wrong while creating channel ' + str(issue.id))
                print('Reason' + str(e))


@tasks.loop(hours=1)  # repeat after every 2 minutes
async def remove_closed_issues():
    await remove_closed_channels()


check_for_new_issues.start()  # Threads
remove_closed_issues.start()  # Threads

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as _e:
        print("Exception found at main worker.\n" + str(_e))
