##############################################
# Package Imports
##############################################
import enum
import math
import random
from discord.ext import commands

##############################################
# Constants and Setup
##############################################
READ_TAG = "r"
START_MSG_PATH = "data/startmessage.txt"

class CreatureType(enum.Enum):
  ALLY = 1,
  ENEMY = 2,
  PLAYER = 3

class Creature:

  def __init__(self, name, init_count , creature_type = CreatureType.PLAYER ):
    self.name = name
    self.initCount = init_count
    self.creatureType = creature_type
    return

class Initiative( commands.Cog, name = "Initiative" ):

  ##############################################
  # Initiative Cog Initialization
  ##############################################
  def __init__( self, bot ):
    self.bot = bot
    self.importStartMessages()
    self.resetInitData()
    
  ##############################################
  # Initiative Cog Commands
  ##############################################
  @commands.group( name = "initiative", aliases = ["init", "i"] )
  async def initiative( self, ctx ):
    if ctx.invoked_subcommand is None:
      await ctx.send( "ERROR: Initiative command(s) improperly invoked. Please see '!s help' for a list of commands and usage examples." )
    return

  @initiative.command( name = "start")
  async def rollInitiative( self, ctx ):
    """
    Allows the collection of initiative order in a 
    discord channel. 
    """
    await self.bot.wait_until_ready()

    if self.activeInitiative:
      await ctx.send("ERROR: Initiative already set! Please use `!s init end` to finish with the current encounter")
      return 

    # Save initialization channel for later use
    self.initChannel = ctx.message.channel

    # Display random start quip
    await self.displayRandStartQuip( ctx )

    await ctx.send("----------")
    await ctx.send("Initiative Tracker is online!\n\nPlease type in '<name> <roll>' into the chat and I'll make a note of it. Example ```'Flint 13' OR\n'13 Flint' OR\n'Diva 13 Thiccums'```")
    await ctx.send("----------")

    # Grab initiative order from the chat
    await self.getInitOrder(ctx)

    # ERROR CASE: No creatures added by the users
    if len(self.initOrder) < 1:
      await ctx.send("ERROR: No creature in initiative order. How are you going to have a fight with no people? Try adding creatures next time.")
      return

    # Display initiative order 
    await self.displayInitOrder( ctx )
    # set active intiative to true, unlocks other commands
    self.activeInitiative = True

    return

  @initiative.command( name = "add" )
  async def addCreatures( self, ctx ):
    """
    Lets the user add creature(s) to an already
    active initiative order 
    """
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return

    await ctx.send("----------")
    await ctx.send("Accepting input for characters!\n\nPlease type in '<name> <roll>' into the chat and I'll make a note of it. Example ```'Flint 13' OR\n'13 Flint' OR\n'Diva 13 Thiccums'```")
    await ctx.send("----------")

    collectInitiative = True 
    while collectInitiative:
      msg = await self.bot.wait_for("message")
      collectInitiative = await self.checkMsg( ctx, msg )
    self.sortInitOrder()
    await self.checkDuplicateCounts( ctx )

    await ctx.send("----------")
    await ctx.send("Character input complete!")
    await self.displayInitOrder( ctx )
    return 

  @initiative.command( name = "display",
  aliases = ["dis", "d", "list","show"])
  async def displayCreatures( self, ctx ):
    """
    Command-level interface for user to display
    initiative order upon request.

    Initiative order must already be set in order
    for this function to work.
    """
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return 
    await self.displayInitOrder( ctx )
    return 

  @initiative.command( name = "edit" ,
  aliases = ["e"])
  async def editCreature( self, ctx ):
    """
    Allows the edit of a creature's initiative count
    while an initiative order is already set
    """
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return

    # Allow the user to designate creature to edit
    acceptingInput = True
    while acceptingInput:

      # Display Initiative Order 
      await self.displayInitOrder( ctx )

      getInput = True
      creature = None
      # While we don't have valid input, loop through
      # and ask the user for input. 
      while getInput:
        await ctx.send("Please type the name of the creature you would like to edit the initiative order for. Type 'nvm' to exit.")
        msg = await self.bot.wait_for("message")
        if msg == "nvm":
          await ctx.send("Alright. I'll be on the lookout for when you do want to remove a creature. Carry on!")
          return
        creature, getInput = self.findCreatureInList( msg )
        
      await ctx.send(f"This is the creature I found:\n**('{creature.initCount}') -{creature.name}**")

      # Check what the user would like to change the count to
      changingCount = True 
      while changingCount:
        await ctx.send("What would you like to change the initiative order to? Plase input a valid number. Type 'nvm' to exit.")
        msg = await self.bot.wait_for("message")
        try:
          if msg.content == "nvm":
            await ctx.send("Alright. I'll be on the lookout for when you do want to edit a creature. Carry on!")
            return
          elif int(msg.content) == creature.initCount:
            await ctx.send("That's the same number it had before... Are you sure you want to change that? Let's double back for a second.")
          else:
            creature.initCount = int(msg.content)
            changingCount = False 
            acceptingInput = False
        except:
          await ctx.send("That's odd. I don't think that was a number. Try again.")

    # Send message confirming update of creature in initiative order
    await ctx.send(f"Creature '{creature.name}' has been updated with initiative count of {creature.initCount}! Your new initiative order is below.")

    self.sortInitOrder()
    await self.displayInitOrder(ctx)

    return 

  @initiative.command( name = "remove" ,
  aliases = ["r","rem"])
  async def removeCreature( self, ctx ):
    """
    Allows the removal of a creature while an 
    initiative order is still active.

    Removed creatures will not be displayed in the
    initiative order, but will still be visible in 
    a separate list when checking. 
    """
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return 

    # Allow the user to designate creature to remove
    acceptingInput = True
    while acceptingInput:

      # Display Initiative Order 
      await self.displayInitOrder( ctx )

      getInput = True
      creature = None
      while getInput:
        await ctx.send("Please type the name of the creature you would like to remove.")
        msg = await self.bot.wait_for("message")
        if msg == "nvm":
          await ctx.send("Alright. I'll be on the lookout for when you do want to remove a creature. Carry on!")
          return
        creature, getInput = self.findCreatureInList( msg )
        

      await ctx.send(f"This is the creature I found:\n**('{creature.initCount}') -{creature.name}**")
      # Confirm removal
      awaitingConfirmation = True 
      while awaitingConfirmation:
        await ctx.send("Are you sure you want to remove this creature (y/n)?")
        msg = await self.bot.wait_for("message")
        if msg.content == "y":
          awaitingConfirmation = False 
          acceptingInput = False
        elif msg.content == "n":
          await ctx.send("Sure. We can go back to make sure you can remove the right creature.")
          awaitingConfirmation = False

    # Remove character from the initiative order
    self.initOrder.remove(creature)
    self.removedCreatures.append(creature)
    await ctx.send(f"Creature '{creature.name}' was removed! Your new initiative order is below.")

    await self.displayInitOrder( ctx )

    return

  @initiative.command( name = "shuffle" )
  async def shuffleCreatures( self, ctx ):
    """
    Allows the shuffling of creature in the initiative order. Less of a necessary functionality and more of a fun option in case it's needed 
    """
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return

    await ctx.send("Alright, you're the boss!")

    newCounts = []
    for creature in self.initOrder:
      newCounts.append(random.randint(1, 30))
    
    random.shuffle(newCounts)
    random.shuffle(self.initOrder)

    i = 0
    for creature in self.initOrder:
      creature.initCount = newCounts[i]
      i += 1

    self.sortInitOrder()
    await ctx.send("Initiative has been shuffled! New order is as follows:")
    await self.displayInitOrder( ctx )

    return

  @initiative.command( name = "end" )
  async def endEncounter( self, ctx ):
    """
    Ends the initiative tracking, allowing for another
    encounter to start if need be.
    """
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return
    await ctx.send("Ending the encounter!")
    await ctx.send("----------")
    await ctx.send("Final Results: ")
    await self.displayInitOrder( ctx )
    self.resetInitData()
    return

  ##############################################
  # Initiative Cog Support Functions
  ##############################################

  # ASYNC SUPPORT FUNCTIONS
  async def checkDuplicateCounts( self, ctx ):
    """
    Checks the initiative count list to ensure there 
    are no duplicates, and handles duplicates by creating
    'decimal initiative'. 
    """
    def check(msg):
      return msg.content == "1" or msg.content == "2"

    noConflicts = False 
    conflict = False
    while not noConflicts:
      totalCreatures = len(self.initOrder)
      conflict = False 
      for i in range(0, totalCreatures):
        if i != totalCreatures - 1:
          creature = self.initOrder[i]
          nextCreature = self.initOrder[i+1]
          if creature.initCount == nextCreature.initCount:
            conflict = True
            messageStr = f"WARNING: One or more creatures has the same initiative count '{creature.initCount}':\n"
            messageStr += f"1. {creature.name}\n"
            messageStr += f"2. {nextCreature.name}\n"
            messageStr += "Which creature would you like to go first (1 or 2)?"
            await ctx.send(messageStr)
            msg = await self.bot.wait_for("message", check=check)

            initStr = str(math.floor(creature.initCount))
            if initStr in self.conflicts:
              self.conflicts[initStr] += 1
            else:
              self.conflicts[initStr] = 1

            newCount = creature.initCount + 1 / (2 * self.conflicts[initStr])
            newCount = round(newCount, 3)
            if msg.content == "1":
              creature.initCount = newCount
              await ctx.send(f"Alright! Creature '{creature.name}' has been updated with an initiative count of '{creature.initCount}'.")
            elif msg.content == "2":
              nextCreature.initCount = newCount
              await ctx.send(f"Alright! Creature '{nextCreature.name}' has been updated with an initiative count of '{nextCreature.initCount}'.")
            break
          elif i + 1 == totalCreatures - 1 and not conflict:
            noConflicts = True
      self.sortInitOrder()

  async def checkMsg(self, ctx, msg):
    """
    Helper function for '!s init start' command.

    Assists with determining whether or not message is 
    properly formatted / has relevant data to add to the initiative order.
    """
    content = msg.content
    channel = msg.channel
    try:

      if channel != self.initChannel:
        return True
      elif content == "done":
        return False

      if "ALLY" in content:
        content = content.replace("ALLY", "")
        ctype = CreatureType.ALLY
      elif "ENEMY" in content:
        content = content.replace("ENEMY", "")
        ctype = CreatureType.ENEMY
      else:
        ctype = CreatureType.PLAYER
        

      numbers = [int(word) for word in content.split() if word.isdigit()]
      words = [word for word in content.split() if not word.isdigit()]
      
      name = ""
      wordCount = 0
      for word in words:
        if wordCount > 0:
          name += " "
        name += word
        wordCount += 1
        
      initCount = numbers[0]
      newCreature = Creature( name, initCount , ctype )
      self.initOrder.append( newCreature )
      await ctx.send(f"Creature '{name}' with initiative count '{initCount}' added!")
      return True 
    except:
      await ctx.send("Huh. That doesn't look right. Try sending it again in the following format. ```<name> <roll> OR <roll> <name>\nExample: 'Flint 13' OR '13 Flint'```")
      return True

  async def displayActiveInitError( self, ctx):
    """
    Displays an error message when initiative is not set.
    """
    await ctx.send("ERROR: There is not a current initiative order set. Please use `!s init start` and set an initiative order before using this command.")
    return 

  async def displayInitOrder( self, ctx ):
    """
    Displays the initiative order in code snippet format on discord.
    """
    # This loop is used to determine the longest # of digits
    # in a single initiative count, in order to make sure they
    # neatly take up the same amount of space
    toplength = 1
    for creature in self.initOrder:
      initStr = str(creature.initCount).replace(".", "")
      digits = len(initStr)
      if digits > toplength:
        toplength = digits
    
    message = "```md\nInitiative Order: \n====================\n"
    for creature in self.initOrder:
      message += self.makeCharString( creature, toplength )
    if len(self.removedCreatures) > 0:
      message += "\nRemoved Creatures: \n====================\n"
      for creature in self.removedCreatures:
        addStr = f"- {creature.name}\n"
        message += addStr

    message += "```"
    await ctx.send(message)
    return

  async def displayRandStartQuip( self , ctx ):
    """
    Helper function for '!s init start'.
    Displays a random 'quip' from various video games
    """
    # Shuffle Quips
    random.shuffle(self.msgList)
    # Get Quip 
    totalQuips = len(self.msgList)
    roll = random.randint(0, totalQuips - 1)
    quip = "\n"
    quip += self.msgList[roll]

    # Send Quip
    await ctx.send(quip)
    return

  async def getInitOrder( self , ctx ):
    """
    Helper Function for '!s init start' command.
    Handles the collecting of initiative until the typing
    of done is completed.
    """
    # Collect initiative 
    collectInitiative = True 
    while collectInitiative:
      msg = await self.bot.wait_for("message")
      collectInitiative = await self.checkMsg( ctx, msg )
    self.sortInitOrder()
    await self.checkDuplicateCounts( ctx )
    await ctx.send("----------")
    await ctx.send("Initiative Order collected!")
    return 

  def findCreatureinList( self, msg ):
    creature = None
    for pos in self.initOrder:
      if msg.content in pos.name:
        creature = pos
    if creature is None:
      return creature, True
    else:
      return creature, False

  def importStartMessages( self ):

    msgList = []

    with open(START_MSG_PATH, READ_TAG) as read_file:
      for line in read_file:
        msgList.append(line)

    self.msgList = msgList

    return

  def makeCharString( self, char , toplength ):

    returnStr = ""

    formatStr = "." + str(toplength - 2) + "f"
    count = str(format(char.initCount, formatStr))
    addStr = ("{:<" + str(toplength + 1) + "}").format(count)
    addStr = addStr.strip()

    if char.creatureType == CreatureType.ALLY:
      returnStr += f"<A>: ({addStr}) - {char.name}\n"
    elif char.creatureType == CreatureType.ENEMY:
      returnStr += f"[E]: ({addStr}) - {char.name}\n"
    elif char.creatureType == CreatureType.PLAYER:
      returnStr += "{P}: "
      returnStr += f"({addStr}) - {char.name}\n"

    return returnStr
  
  def resetInitData( self ):
    """
    Resets relevant stored data to default setting for
    initiative tracking
    """
    self.activeInitiative = False 
    self.conflicts = {}
    self.initChannel = None
    self.initOrder = []
    self.removedCreatures = []
    return

  def sortInitOrder( self ):
    """
    Sorts the initiative order from highest value to lowest.
    """
    self.initOrder.sort(
      key = lambda x: x.initCount, 
      reverse = True
    )
    return
  
##############################################
# Setup Function for Cog
##############################################
def setup( bot ):
  print("Attempting load of 'initiative' extension...")
  bot.add_cog( Initiative( bot ) )