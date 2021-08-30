##############################################
# Package Imports 
##############################################
import discord 

from discord.ext import commands
from replit import db

##############################################
# Constants
##############################################

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
  "882041917154656307",
  "882042443527225384"
]

##############################################
# ReactRoles Cog
##############################################

class ReactRoles( commands.Cog, name = "reactroles" ):

  def __init__( self, bot ):
    self.bot = bot 

  ##############################################
  # ReactRoles Events
  ##############################################
  @commands.Cog.listener()
  async def on_raw_reaction_add( self, RawReactionActionEvent ):

    reaction = RawReactionActionEvent
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

  async def assignPronounRole( self, guild, user , emoji ):

    for roleStr in PRONOUN_ROLES:
      role = discord.utils.get( guild.roles, name = roleStr)
      if role in user.roles:
        await user.remove_roles( role )

    roleStr = PRONOUN_ROLES[PRONOUN_EMOJI.index(emoji)]
    role = discord.utils.get( guild.roles, name = roleStr )
    await user.add_roles( role )

    await user.send(f"Awesome! Your selected pronouns `{roleStr}` have been added to your list of roles on `The Backrooms`.")
    print(f"User '{user.display_name}' assigned role '{roleStr}'")

    return

  async def assignRegionRole( self, guild, user, emoji ):

    for roleStr in REGION_ROLES:
      role = discord.utils.get( guild.roles, name = roleStr)
      if role in user.roles:
        await user.remove_roles( role )

    roleStr = REGION_ROLES[REGION_EMOJI.index(emoji)]
    role = discord.utils.get( guild.roles, name = roleStr )
    await user.add_roles( role )

    await user.send(f"Great! Your selected region `{roleStr}` have been added to your list of roles on `The Backrooms`.")
    print(f"User '{user.display_name}' assigned role '{roleStr}'")

    return

##############################################
# Setup Command for Bot
##############################################
def setup(bot):
  print("Attempting load of 'reactroles' extension...")
  bot.add_cog( ReactRoles( bot ) )