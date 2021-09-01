##############################################
# Package Imports 
##############################################
import discord 

from discord import Guild, Member, RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Bot

from log import ConsoleLog

##############################################
# Constants
##############################################

GENERAL_CHANNEL_ID = "703015465567518802"

MEMBER_EMOJI = "✅"
MEMBER_ROLE = "Member"

MODULE = "REACTROLES"

PRONOUN_EMOJI = [
  "☀️", "🌙", "✨", "🪐"
]
PRONOUN_ROLES = [
  "He/Him", "She/Her", "They/Them", "Any/All Pronouns"
]
REGION_EMOJI = [
  "🟢", "🟣", "⚪", "🔵", "🟤", "🟠", "🔴"
]
REGION_ROLES = [
  "Europe", "North America", "South America", "Oceanic", 
  "Russia", "Asia", "Africa"
]

REACT_ROLE_MSG_IDS = [
  "882041917154656307", # Pronouns
  "882042443527225384", # Region
  "882309606611767326"  # Memeber Confirmation
]

##############################################
# ReactRoles Cog
##############################################

class ReactRoles( commands.Cog, name = "reactroles" ):

  def __init__( self, bot: Bot ):
    self.bot = bot 
    self.logging = ConsoleLog()


  ##############################################
  # ReactRoles Events
  ##############################################
  @commands.Cog.listener()
  async def on_raw_reaction_add( self, payload: RawReactionActionEvent ) -> None:

    reaction = payload
    channelID = str(reaction.channel_id)
    channel = await self.bot.fetch_channel(channelID)
    messageID = str(reaction.message_id)
    message = await channel.fetch_message(messageID)
    userID = str(reaction.user_id)
    user = await message.guild.fetch_member(userID)
    emoji = str(reaction.emoji)

    if messageID not in REACT_ROLE_MSG_IDS:
      return
    if user == self.bot.user or user.bot:
      return

    if emoji == MEMBER_EMOJI:
      await self.assignMemberRole(
        message.guild, user )
    if emoji in PRONOUN_EMOJI:
      await self.assignPronounRole( message.guild, user , emoji )
    elif emoji in REGION_EMOJI:
      await self.assignRegionRole( message.guild, user, emoji )

    await message.remove_reaction( emoji, user )

    return 

  ##############################################
  # ReactRoles Support Functions
  ##############################################

  # ASYNC SUPPORT FUNCTIONS

  async def assignMemberRole( self, guild: Guild, member: Member ) -> None:
    """
    Assigns the member role to a given user in a given guild.
    """
    self.logging.send( MODULE , f"Attempting to assign 'Member' role to user '{member}'" )

    role = discord.utils.get( guild.roles , name = MEMBER_ROLE )
    if role not in member.roles:
      # Notify user that they are now a member
      await member.add_roles( role )
      await member.send("Thank you for reading and agreeing to our rules! You've been given member privileges on `The Backrooms`~")
      await member.send("Feel free to introduce yourself in `#introductions` and/or grab a role or two in `#self-roles`!")

      # Output to console
      self.logging.send( MODULE, f"'Member' role assigned to {member}!" )

      # Send Message to General Chat
      channel = await guild.fetch_channel(GENERAL_CHANNEL_ID)
      await channel.send(f"Howdy {member.mention}! Welcome to The Backrooms discord server!! Take a look at {channel.mention} if you want to choose a class, pronouns, or show off what region you're from. Feel free to message this channel if you are unsure about anything or if you have any questions.")
    else:
      self.logging.send( MODULE, f"User '{member}' already has role 'Member'." )
    return 

  async def assignPronounRole( self, guild: Guild, member: Member, emoji: str ) -> None :
    """
    Assigns a specific pronoun role to a given user in a given server, depending on given emoji string.
    """
    for roleStr in PRONOUN_ROLES:
      role = discord.utils.get( guild.roles, name = roleStr)
      if role in member.roles:
        await member.remove_roles( role )

    roleStr = PRONOUN_ROLES[PRONOUN_EMOJI.index(emoji)]
    role = discord.utils.get( guild.roles, name = roleStr )
    await member.add_roles( role )

    await member.send(f"Awesome! Your selected pronouns `{roleStr}` have been added to your list of roles on `The Backrooms`.")
    self.logging.send( MODULE, f"User '{member.display_name}' assigned role '{roleStr}'")

    return

  async def assignRegionRole( self, guild: Guild, member: Member, emoji: str ) -> None:
    """
    Assigns a specific region role to a given user on a given server, depending on given emoji string.
    """
    for roleStr in REGION_ROLES:
      role = discord.utils.get( guild.roles, name = roleStr )
      if role in member.roles:
        await member.remove_roles( role )

    roleStr = REGION_ROLES[REGION_EMOJI.index(emoji)]
    role = discord.utils.get( guild.roles, name = roleStr )
    await member.add_roles( role )

    await member.send(f"Great! Your selected region `{roleStr}` have been added to your list of roles on `The Backrooms`.")
    self.logging.send( MODULE, f"User '{member.display_name}' assigned role '{roleStr}'")

    return

##############################################
# Setup Command for Bot
##############################################
def setup( bot: Bot ) -> None:
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( ReactRoles( bot ) )