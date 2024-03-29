import discord
import embeds

logger = None


# RULES_REACT
async def on_react(bot, rules_channel, user, ticket_channel, logger):
    logger.info('bot called for ' + str(user.id) + "/" + user.name)
    # change role of the person
    try:
        await user.add_roles(discord.utils.get(rules_channel.guild.roles, name='waiting'))
    except Exception as _err:
        err_msg = embeds.error_embed("", "Error assigning the role.\nIf you are an admin, check logs to rectify the "
                                         "issue")
        await rules_channel.send(embed=err_msg, delete_after=60)
        raise Exception(str(_err))

    # TODO => Mention channels of onboarding here
    suc_msg = embeds.simple_embed("Success", "Congratulations " + user.mention + "\nPlease head to the channel that "
                                                                                 "suits you well.")
    await rules_channel.send(embed=suc_msg, delete_after=60)
    logger.success(str(user.id) + "/" + user.name + " successfully added to the waiting list.")
