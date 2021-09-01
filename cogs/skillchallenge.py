##############################################
# Package Imports
##############################################

import random

from discord.ext import commands

from log import ConsoleLog
from sc_classes import SC_Instance

##############################################
# Constants and Setup
##############################################

MODULE = "SKILLCHALLENGE"

class SkillChallenge( commands.Cog, name = "Skill Challenge" ):

  ##############################################
  # SkillChallenge Cog Initialization
  ##############################################
  def __init__(self, bot):
    self.bot = bot
    self.instances = {}
  
  ##############################################
  # SkillChallenge Cog Commands
  ##############################################
  @commands.group( name = "skillchallenge", aliases = ["sc"] )
  async def skillchallenge( self, ctx ):
    if ctx.invoked_subcommand is None:
      await ctx.send( "ERROR: Skill Challenge command(s) improperly invoked. Please see '!help' for a list of commands and usage examples." )
    return

  @skillchallenge.command( name = "start" )
  async def startSC( self, ctx ):
    """
    Must not already have an active skill challenge.

    Allows the creation of a skill challenge. The Traveler will walk you
    through how to do that through questions and example input. 
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)
    if not self.checkActiveInstance( channel ):
      self.instances[channel] = SC_Instance( self.bot )
    else:
      await self.displayActiveSCError( ctx )
      return

    sc = self.instances[channel]

    await sc.start( ctx )
    
    return

  @skillchallenge.command( name = "add" )
  async def addSCAction( self, ctx ):
    """
    Must have an active skill challenge to use.

    Allows the user to add an action of different types (attack, item, skill, spell, or other) and determine success/failure.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkActiveInstance( channel ):
      await self.displayNoActiveSCError( ctx )
      return 

    sc = self.instances[channel]

    await sc.addAction( ctx )

    return 

  @skillchallenge.command( name = "display" , aliases = ["d","dis"] )
  async def displaySC( self, ctx ):
    """
    Must have an active skill challenge to use.

    Command-level interface for users to see the current 
    information regarding the skill challenge.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkActiveInstance( channel ):
      await self.displayNoActiveSCError( ctx )
      return 

    sc = self.instances[channel]

    await sc.displaySCStats( ctx )

    return

  @skillchallenge.command( name = "end" )
  async def endSC( self, ctx ):
    """
    Must have a skill challenge already active.

    Ends the current skill challenge tracking, outputting the current
    status back to the user and reseting internal variables.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkActiveInstance( channel ):
      await self.displayNoActiveSCError( ctx )
      return 

    sc = self.instances[channel]

    await sc.end( ctx )

    del self.instances[channel]

    return

  ##############################################
  # Initiative Sub Commands
  ##############################################

  @skillchallenge.group( name = "init" )
  async def initiative( self, ctx ):
    if ctx.invoked_subcommand is None:
      await ctx.send( "ERROR: Skill Challenge command(s) improperly invoked. Please see '!help' for a list of commands and usage examples." )
    return

  @initiative.command( name = "add" )
  async def addSCInitCreature( self, ctx ):
    """
    Must have a skill challenge active in order to use. 
    Allows the addition of creatures to the initiative order after the initiative has been set.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkActiveInstance( channel ):
      await self.displayNoActiveSCError( ctx )
      return 

    sc = self.instances[channel]

    await sc.addInitCreature( ctx )

    return

  @initiative.command( name = "edit" )
  async def editSCInitOrder( self, ctx ):
    """
    Must have an active skill challenge to use.
    Allows the editing of initiative count for a creature in the order.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkActiveInstance( channel ):
      await self.displayNoActiveSCError( ctx )
      return 

    sc = self.instances[channel]

    await sc.editInitCreature( ctx )

    pass

  @initiative.command( name = "remove" )
  async def removeCreatureFromSCInitOrder( self, ctx ):
    """
    Must have an active skill challenge to use.

    Allows the removal of a creature from the initiative order. Creatures are still visible when the skill challenge is displayed under 'Removed Creatures'
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkActiveInstance( channel ):
      await self.displayNoActiveSCError( ctx )
      return 

    sc = self.instances[channel]

    await sc.removeInitCreature( ctx )

    return

  @initiative.command( name = "shuffle" )
  async def shuffleSCOrder( self, ctx ):
    """
    Requires an active initiative order to use.
    Allows the shuffling of the initiative order. Mostly just for 
    fun, since it's doubtful that situation would happen in combat.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkActiveInstance( channel ):
      await self.displayNoActiveSCError( ctx )
      return 

    sc = self.instances[channel]

    await sc.shuffleInitCreatures( ctx )

    return 

  ##############################################
  # Support Functions 
  ##############################################
  async def displayActiveSCError( self, ctx):
    """
    Displays an error message when skill challenge is already set.
    """
    await ctx.send("ERROR: There is already a current challenge set. Please use `!sc end` before using this command.") 
    return 

  async def displayNoActiveSCError( self, ctx):
    """
    Displays an error message when skill challenge is not set.
    """
    await ctx.send("ERROR: There is not a current skill challenge set. Please use `!sc start` and set that up before using this command.") 
    return 

  # ASYNC SUPPORT FUNCTIONS 
  def checkActiveInstance( self, channel: str ) -> bool:
    keys = self.instances.keys()
    if channel in keys:
      return True
    return False

  # SYNCHRONOUS SUPPORT FUNCTIONS
  
  

  # End of SkillChallenge Cog

##############################################
# Setup Function for SkillChallenge Cog
##############################################
def setup( bot ):
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( SkillChallenge( bot ) )