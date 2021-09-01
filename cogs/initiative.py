##############################################
# Package Imports
##############################################
from discord.ext import commands
from discord.ext.commands import Context

from initiativeclasses import InitiativeInstance
from log import ConsoleLog

##############################################
# Constants and Setup
##############################################
MODULE = "INITIATIVE"

class Initiative( commands.Cog, name = "Initiative" ):

  ##############################################
  # Initiative Cog Initialization
  ##############################################
  def __init__( self, bot ):
    self.bot = bot
    self.logging = ConsoleLog()
    self.instances = {}
    
  ##############################################
  # Initiative Cog Commands
  ##############################################
  @commands.group( name = "initiative", aliases = ["init", "i"] )
  async def initiative( self, ctx: Context ) -> None:
    if ctx.invoked_subcommand is None:
      await ctx.send( "ERROR: Initiative command(s) improperly invoked. Please see '!help' for a list of commands and usage examples." )
    return

  @initiative.command( name = "start")
  async def rollInitiative( self, ctx: Context ) -> None:
    """
    Allows the collection of initiative order in a 
    discord channel. 
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)
    if not self.checkIfActiveInstance( channel ):
      self.instances[channel] = InitiativeInstance( self.bot )
    else:
      await ctx.send("ERROR: There is not a current initiative order set. Please use `!init start` and set an initiative order before using this command.")
      return

    initiative = self.instances[channel]

    await initiative.start( ctx )
    return

  @initiative.command( name = "add" )
  async def addCreatures( self, ctx: Context ) -> None :
    """
    Lets the user add creature(s) to an already
    active initiative order 
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkIfActiveInstance( channel ):
      await self.displayActiveInitError( ctx )
      return

    initiative = self.instances[channel]

    await initiative.addCreatures( ctx )
    return 

  @initiative.command( name = "display", aliases = ["dis", "d", "list","show"] )
  async def displayCreatures( self, ctx: Context ) -> None:
    """
    Command-level interface for user to display
    initiative order upon request.

    Initiative order must already be set in order
    for this function to work.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkIfActiveInstance( channel ):
      await self.displayActiveInitError( ctx )
      return

    initiative = self.instances[channel]

    await initiative.displayInitOrder( ctx )
    return 

  @initiative.command( name = "edit" , aliases = ["e"] )
  async def editCreature( self, ctx: Context ) -> None:
    """
    Allows the edit of a creature's initiative count
    while an initiative order is already set
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkIfActiveInstance( channel ):
      await self.displayActiveInitError( ctx )
      return

    initiative = self.instances[channel]

    await initiative.editCreatures( ctx )
    return 

  @initiative.command( name = "remove" , aliases = ["r","rem"] )
  async def removeCreature( self, ctx: Context ) -> None:
    """
    Allows the removal of a creature while an 
    initiative order is still active.

    Removed creatures will not be displayed in the
    initiative order, but will still be visible in 
    a separate list when checking. 
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkIfActiveInstance( channel ):
      await self.displayActiveInitError( ctx )
      return

    initiative = self.instances[channel]

    await initiative.removeCreatures( ctx )
    return

  @initiative.command( name = "shuffle" )
  async def shuffleCreatures( self, ctx ):
    """
    Allows the shuffling of creature in the initiative order. Less of a necessary functionality and more of a fun option in case it's needed 
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkIfActiveInstance( channel ):
      await self.displayActiveInitError( ctx )
      return

    initiative = self.instances[channel]

    await initiative.shuffleInitOrder( ctx )
    return

  @initiative.command( name = "end" )
  async def endEncounter( self, ctx ):
    """
    Ends the initiative tracking, allowing for another
    encounter to start if need be.
    """
    await self.bot.wait_until_ready()

    channel = str(ctx.channel.id)

    if not self.checkIfActiveInstance( channel ):
      await self.displayActiveInitError( ctx )
      return

    initiative = self.instances[channel]

    await initiative.end( ctx )

    del self.instances[channel]

    return

  def checkIfActiveInstance( self , channel: str):
    keys = self.instances.keys()
    if channel not in keys:
      return False 
    return True

  async def displayActiveInitError( self, ctx):
    """
    Displays an error message when initiative is not set.
    """
    await ctx.send("ERROR: There is not a current initiative order set. Please use `!init start` and set an initiative order before using this command.") 
    return 

  
##############################################
# Setup Function for Cog
##############################################
def setup( bot ):
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( Initiative( bot ) )