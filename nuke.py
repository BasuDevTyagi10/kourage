import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command()
async def role_kick(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Client')
    for member in ctx.guild.members:
        print(member)
        if role not in member.roles:
            try:
                embed = discord.Embed(title="Koders Korporation",
                                      description="<br /> We are conducting a server maintenance for reasons you don’t really care about. If you have been kicked from the server and received this message, then we were unable to find your position. Nevertheless, join our brand-new servers as per your role. ♫Never gonna give you up Never gonna let you down♫",
                                      color=0x008cb4)
                embed.set_author(name="Notice [Important]")
                await member.send(embed=embed)

                embed = discord.Embed(title="Clients and Prospects", url="https://discord.gg/DBqcyS6b",
                                      description="Join this server to see what the Koders is cooking and for onboarding on new projects.",
                                      color=0x008cb4)
                await member.send(embed=embed)

                embed = discord.Embed(title="Koders’ Placement Center", url="https://discord.gg/V8vvqvnP",
                                      description="Join this server if you are looking to become a Koders’ Knight (Its as cool as being an actual knight). Find all hiring related information and services here.",
                                      color=0x006d8f)
                await member.send(embed=embed)

                embed = discord.Embed(title="Kore Knights", url="https://discord.gg/6YtHmq8g",
                                      description="For all the current and alumni Knights, join here for to flex your work, post inside jokes, and talk about nerd stuff, ya nerd (and internal updates too).",
                                      color=0x006d8f)
                await member.send(embed=embed)

                await member.kick(reason="No longer supported")
            except Exception as e:
                print(e)

bot.run('')
