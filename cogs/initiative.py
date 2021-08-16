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

startMessages = [
  'Open the Game!',
  'Mankind knew they could not change society. So instead of reflecting on themselves, they blamed the Beasts.\nHEAVEN OR HELL\nDUEL 1\nLET\'S ROCK!',
  'Work together, and you might survive.',
  'The enemy is all around you.',
  'The Iron Lords are watching, Guardians.',
  'How will you fare against utter chaos?',
  'Once more unto the breach!',
  'It\'s time to kick ass and chew bubble gum... and you\'re all out of gum.',
  'Would you kindly start the encounter?',
  'Remove any doubts in your head. It\'s you or them.',
  'Are we rushing in? Or are we going sneaky-beaky like?',
  'For Queen and country, men!',
  'For King and country, men!',
  'These fellas are gonna regret waking up this morning.',
  'Gentlemen and Ladies, it\'s time to fight!',
  'Ladies and gentlemen, let\'s get ready to rumble!',
  'Time to wrestle like bear!',
  'Can\'t escape from crossing fate. Fight!',
  'The wheel of fate is turning! Rebel 1! ACTION!!',
  'Put on a show!\nWORLD IS A FUCK\nFirst Regret, Let\'s GET IT, CRACKERS!!',
  'Stay focused, stay alive.',
  'Busy night...but there\'s always room for another!',
  'Everyone! Get in here!',
  'Liadrin! Versus! Jaina!\n...wait. That\'s the wrong one. Just start the encounter...',
  'The right people in the wrong place can make all the difference in the world.',
  'No gods or kings, only man. Get on with it.',
  'If our lives are already written, it would take courageous souls to change the script.',
  'Do you think love can bloom, even on a battlefield?',
  'If we are to be swallowed by fate, we must have fought well.',
  'The courage to walk into the Darkness, but strength to return to the Light.',
  'Nothing is true, everything is permitted.',
  'NOTHING IS MORE BADASS THAN TREATING WOMEN WITH RESPECT! *guitar solo*',
  'It\'s dangerous to go alone, take this!',
  'Often when we guess at other\'s motives, we reveal only our own.',
  'Endure and survive.',
  'You can\'t undo what you\'ve already done, but you can face up to it.',
  'Life is all about resolve. Outcome is secondary.',
  'What is a man? A miserable little pile of secrets. But whatever, have at you!',
  'A man chooses, a slave obeys.',
  'Grass grows, birds fly, sun shines, and brother, you guys hurt people.',
  'It\'s more important to master the cards you\'re holding than to complain about the ones your opponents were dealt.',
  'What is a man but the sum of his memories? We are the stories we live! The tales we tell ourselves!',
  "When life gives you lemons, don't make lemonade. Make life take the lemons back! Get mad! I don't want your damn lemons! What am I supposed to do with these?! Demand to see life's manager! Make life rue the day it thought it could give Cave Johnson lemons! Do you know who I am?! I'm the man who's gonna burn your house down! With the lemons! I'm gonna get my engineers to invent a combustible lemon that burns your house down!",
  "Do you *like* hurting other people?",
  "What is bravery, without a dash of recklessness?",
  "Panasonic Blu-Ray $499... Hh yep. That\'s the wrong paper. Ignore that, please.",
  "Can the defiled be consecrated? Can the fallen find rest?",
  "I knew all of these paths once; now they are as twisted as man\'s ambitions."
  "Driving out corruption is an endless battle, but one that must be fought.",
  "A spark without kindling is a goal without hope.",
  "Cruel machinations spring to life with a singular purpose!",
  "The blood pumps, the limbs obey!",
  "Death is patient, it will wait.",
  "Prodigious size alone does not dissuade the sharpened blade",
  "The bigger the beast, the greater the glory.",
  "Death waits for the slightest lapse in concentration.",
  "A brilliant confluence of skill and purpose!",
  "These nightmarish creatures can be felled! They can be beaten!",
  "Success so clearly in view... or is it merely a trick of the light?",
  "Remind yourself that overconfidence is a slow and insidious killer."
]

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
    if self.activeInitiative:
      await ctx.send("ERROR: Initiative already set! Please use `!s init end` to finish with the current encounter")
      return 
    self.initChannel = ctx.message.channel
    await self.displayRandStartQuip( ctx )
    await ctx.send("----------")
    await ctx.send("Initiative Tracker is online!\n\nPlease type in '<name> <roll>' into the chat and I'll make a note of it. Example ```'Flint 13' OR\n'13 Flint' OR\n'Diva 13 Thiccums'```")
    await ctx.send("----------")
    await self.getInitOrder(ctx)
    # ERROR CASE: No creatures added by the users
    if len(self.initOrder) < 1:
      await ctx.send("ERROR: No creature in initiative order. How are you going to have a fight with no people? Try adding creatures next time.")
      return
    await self.displayInitOrder( ctx )
    self.activeInitiative = True
    return

  @initiative.command( name = "add" )
  async def addCreatures( self, ctx ):
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
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return

    def checkValidInput( msg ):
      creature = None
      for pos in self.initOrder:
        if msg.content in pos.name:
          creature = pos
      if creature is None:
        return creature, True
      else:
        return creature, False

    # Allow the user to designate creature to edit
    acceptingInput = True
    while acceptingInput:

      # Display Initiative Order 
      await self.displayInitOrder( ctx )

      getInput = True
      creature = None
      while getInput:
        await ctx.send("Please type the name of the creature you would like to edit the initiative order for.")
        msg = await self.bot.wait_for("message")
        if msg == "nvm":
          await ctx.send("Alright. I'll be on the lookout for when you do want to remove a creature. Carry on!")
          return
        creature, getInput = checkValidInput( msg )
        

      await ctx.send(f"This is the creature I found:\n**('{creature.initCount}') -{creature.name}**")
      # Confirm removal
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

    # Remove character from the initiative order
    await ctx.send(f"Creature '{creature.name}' has been updated with initiative count of {creature.initCount}! Your new initiative order is below.")

    self.sortInitOrder()
    await self.displayInitOrder(ctx)

    return 

  @initiative.command( name = "remove" ,
  aliases = ["r","rem"])
  async def removeCreature( self, ctx ):
    if not self.activeInitiative:
      await self.displayActiveInitError( ctx )
      return 

    def checkValidInput( msg ):
      creature = None
      for pos in self.initOrder:
        if msg.content in pos.name:
          creature = pos
      if creature is None:
        return creature, True
      else:
        return creature, False

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
        creature, getInput = checkValidInput( msg )
        

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
  async def displayActiveInitError( self, ctx):
    """
    Displays an error message when initiative is not set.
    """
    await ctx.send("ERROR: There is not a current initiative order set. Please use `!s init start` and set an initiative order before using this command.")
    return 

  async def displayRandStartQuip( self , ctx ):
    """
    Helper function for '!s init start'.
    Displays a random 'quip' from various video games
    """
    # Shuffle Quips
    random.shuffle(startMessages)
    # Get Quip 
    totalQuips = len(startMessages)
    roll = random.randint(0, totalQuips - 1)
    quip = "\n"
    quip += startMessages[roll]

    # Send Quip
    await ctx.send(quip)
    return

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