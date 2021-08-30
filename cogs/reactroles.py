##############################################
# Package Imports 
##############################################
import discord 

from discord.ext import commands
from replit import db

##############################################
# Constants
##############################################

CLASS_EMOJI = ["🎶", "⚔️", "🪄", "🛡️", "🏹", "🗡️", "☠️"]

REACT_ROLE_MSG_IDS = [
  "882013329411948606"
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

    return 


  ##############################################
  # ReactRoles Commands
  ##############################################

  

  

##############################################
# Setup Command for Bot
##############################################
def setup(bot):
  print("Attempting load of 'reactroles' extension...")
  bot.add_cog( ReactRoles( bot ) )