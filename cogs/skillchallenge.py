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

COMPLICATION_MOD_EASY = 2
COMPLICATION_MOD_MODERATE = 4
COMPLICATION_MOD_HARD = 6
COMPLICATION_MOD_DAUNTING = 8
COMPLICATION_MOD_FORMIDABLE = 10

EASY_DC = 10
MODERATE_DC = 15
HARD_DC = 20

TIER_1_STR = "Local Heroes (1-4th level)"
TIER_2_STR = "Heroes of the Realm (5-9th level)"
TIER_3_STR = "Masters of the Realm (10-14th level)"
TIER_4_STR = "Masters of the World (15-20th+ level)"

tierData = {
  1 : {
    "spellSuccessLevel" : 1,
    1 : {
      "skillDC" : EASY_DC,
      "successLimit" : 4
    },
    2 : {
      "skillDC" : EASY_DC,
      "successLimit" : 6
    },
    3 : {
      "skillDC" : MODERATE_DC,
      "successLimit" : 5
    }
  },
  2 : {
    "spellSuccessLevel" : 3,
    1 : {
      "skillDC" : EASY_DC,
      "successLimit" : 7
    },
    2 : {
      "skillDC" : MODERATE_DC,
      "successLimit" : 5
    },
    3 : {
      "skillDC" : MODERATE_DC,
      "successLimit" : 7
    }
  },
  3 : {
    "spellSuccessLevel" : 6,
    1 : {
      "skillDC" : MODERATE_DC,
      "successLimit" : 4
    },
    2 : {
      "skillDC" : MODERATE_DC,
      "successLimit" : 6
    },
    3 : {
      "skillDC" : HARD_DC,
      "successLimit" : 4
    }
  },
  4 : {
    "spellSuccessLevel" : 6,
    1 : {
      "skillDC" : MODERATE_DC,
      "successLimit" : 6
    },
    2 : {
      "skillDC" : HARD_DC,
      "successLimit" : 5
    },
    3 : {
      "skillDC" : HARD_DC,
      "successLimit" : 6
    }
  }
}

class SC_CreatureType(enum.Enum):
  ALLY = 1,
  COMPLICATION = 2,
  ENEMY = 3,
  PLAYER = 4

class SC_Creature:

  def __init__(self, name, initCount, creatureType = SC_CreatureType.PLAYER ):
    self.name = name 
    self.initCount = initCount
    self.creatureType = creatureType
    return 

class SC_ActionType(enum.Enum):
  ATTACK = 1,
  ITEM = 2,
  SKILL = 3,
  SPELL = 4,
  OTHER = 5

class SC_LockableSkill:

  def __init__( self, name, action_type = SC_ActionType.SKILL ):
    self.name = name 
    self.actionType = action_type
    return

class SC_TierData:

  def __init__( self, name, comp_mod, tier , difficulty ):
    self.name = name
    self.compMod = comp_mod
    self.difficulty = difficulty 
    self.tier = tier 
    self.setTierVars()

  def setTierVars( self ):
    varData = tierData[self.tier]
    self.spellSuccessLevel = varData["spellSuccessLevel"]
    self.skillDC = varData[self.difficulty]["skillDC"]
    self.successLimit = varData[self.difficulty]["successLimit"]

SC_TIER1_D1 = SC_TierData( "Local Heroes (1-4th level) - Easy Difficulty", COMPLICATION_MOD_EASY, 1, 1)
SC_TIER1_D2 = SC_TierData( "Local Heroes (1-4th level) - Medium Difficulty", COMPLICATION_MOD_EASY, 1, 2)
SC_TIER1_D3 = SC_TierData( "Local Heroes (1-4th level) - Hard Difficulty", COMPLICATION_MOD_EASY, 1, 3)
SC_TIER2_D1 = SC_TierData( "Heroes of the Realm (5-9th level) - Easy Difficulty", COMPLICATION_MOD_MODERATE, 2, 1)
SC_TIER2_D2 = SC_TierData( "Heroes of the Realm (5-9th level) - Medium Difficulty", COMPLICATION_MOD_MODERATE, 2, 2)
SC_TIER2_D3 = SC_TierData( "Heroes of the Realm (5-9th level) - Hard Difficulty", COMPLICATION_MOD_MODERATE, 2, 3)
SC_TIER3_D1 = SC_TierData( "Masters of the Realm (10-14th level) - Easy Difficulty", COMPLICATION_MOD_HARD, 3, 1)
SC_TIER3_D2 = SC_TierData( "Masters of the Realm (10-14th level) - Medium Difficulty", COMPLICATION_MOD_HARD, 3, 2)
SC_TIER3_D3 = SC_TierData( "Masters of the Realm (10-14th level) - Hard Difficulty", COMPLICATION_MOD_HARD, 3, 3)
SC_TIER4_D1 = SC_TierData( "Masters of the World (15-20th+ level) - Easy Difficulty", COMPLICATION_MOD_DAUNTING, 4, 1)
SC_TIER4_D2 = SC_TierData( "Masters of the World (15-20th+ level) - Medium Difficulty", COMPLICATION_MOD_DAUNTING, 4, 2)
SC_TIER4_D3 = SC_TierData( "Masters of the World (15-20th+ level) - Hard Difficulty", COMPLICATION_MOD_FORMIDABLE, 4, 3)

class SkillChallenge(
  commands.Cog,
  name = "Skill Challenge" ):

  ##############################################
  # SkillChallenge Cog Initialization
  ##############################################
  def __init__(self, bot):
    self.bot = bot
    self.failLimit = 3
    self.resetSCVars()
  
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
    through 
    """
    await self.bot.wait_until_ready()

    if self.activeSC:
      await self.displayNoActiveSCError( ctx )
      return 

    self.initChannel = ctx.message.channel

    async def checkForValidTier( ctx, msg ):
      collectingTier = None
      tier = 0
      try:
        tier = int( msg.content )
        if tier < 1 or tier > 4:
          await ctx.send("Sorry, that number is outside of the given range. Please try a number between 1-4.")
          collectingTier = True
        else:
          collectingTier = False 
      except:
        await ctx.send("Wait a second, that's not a valid number. Try taking a look at the list of possible options and try again.")
        collectingTier = True 
      return collectingTier, tier

    # Choose a tier of play
    displayStr = f"```md\n1. {TIER_1_STR}\n2. {TIER_2_STR}\n"
    displayStr += f"3. {TIER_3_STR}\n4. {TIER_4_STR}\n```"
    await ctx.send(displayStr)
    await ctx.send("Which tier of play would you like to use (1-4)?")
    collectingTier = True 
    while collectingTier:
      msg = await self.bot.wait_for("message")
      collectingTier, tier = await checkForValidTier( ctx, msg )

    async def checkForValidDifficulty( ctx, msg ):
      collectingDifficulty = None
      difficulty = 0
      try:
        difficulty = int( msg.content )
        if difficulty < 1 or difficulty > 3:
          await ctx.send("Sorry, that number is outside of the given range. Please try a number between 1-3.")
          collectingDifficulty = True 
        else:
          collectingDifficulty = False
      except:
        await ctx.send("Wait a second, that's not a valid number. Try taking a look at the list of possible options and try again.")
        collectingDifficulty = True 
      return collectingDifficulty, difficulty

    # Choose a difficulty setting
    displayStr = f"```md\n1. Easy\n2. Medium\n3. Hard\n```"
    await ctx.send(displayStr)
    await ctx.send("What difficulty will this challenge be (1-3)?")
    collectingDifficulty = True 
    while collectingDifficulty:
      msg = await self.bot.wait_for("message")
      collectingDifficulty, difficulty = await checkForValidDifficulty( ctx, msg )

    presetStr = f"SC_TIER{tier}_D{difficulty}"
    self.tierData = globals()[presetStr]
    self.successLimit = self.tierData.successLimit

    # Collect initiative order
    await ctx.send("----------")
    await ctx.send("Accepting input for characters!\n\nPlease type in '<name> <roll>' into the chat and I'll make a note of it. Example ```'Flint 13' OR\n'13 Flint' OR\n'Diva 13 Thiccums'```")
    await ctx.send("----------")
    await self.getInitOrder( ctx )

    self.sortInitOrder()
    await self.checkDuplicateCounts( ctx )

    await ctx.send("----------")
    await ctx.send("Skill Challenge initiated!")

    await self.displaySCStats( ctx )

    # Display order + used skills to the users
    self.activeSC = True 
    return

  @skillchallenge.command( name = "add" )
  async def addSCAction( self, ctx ):

    # TODO: Implement !sc add command

    await self.bot.wait_until_ready()

    if not self.activeSC:
      await self.displayNoActiveSCError( ctx )
      return 

    # Ask what type of action this is
    # - Resolve based on what type of action it is

    # Ask the roll for that action 

    # Output a success / failure

    # Display current status to the party
    pass


  @skillchallenge.command( name = "init add")
  async def addSCInitCreature( self, ctx ):
    # TODO: Implement !sc init add command
    pass

  @skillchallenge.command( name = "display" )
  async def displaySC( self, ctx ):
    """
    Must have an active skill challenge to use.

    Command-level interface for users to see the current 
    information regarding the skill challenge.
    """
    await self.bot.wait_until_ready()

    if not self.activeSC:
      await self.displayNoActiveSCError( ctx )
      return 

    await self.displaySCStats( ctx )

    pass

  @skillchallenge.command( name = "init edit" )
  async def editSCInitOrder( self, ctx ):

    # TODO: Implement !sc init edit command

    await self.bot.wait_until_ready()

    if not self.activeSC:
      await self.displayNoActiveSCError( ctx )
      return 

    # Ask which creature to change

    # Output found creature to the user

    # Ask what they would like to change the order to

    # Change that creature's initiative order

    # Display the new initiative order

    pass

  @skillchallenge.command( name = "shuffle" )
  async def shuffleSCOrder( self, ctx ):

    # TODO: Implement !sc init shuffle command

    await self.bot.wait_until_ready()

    if not self.activeSC:
      await self.displayNoActiveSCError( ctx )
      return 

    # Grab the list of creaturews

    # Generate new initiative 

    # Shuffle lists

    # Assign new counts

    # Display new order to the user.

    pass

  @skillchallenge.command( name = "end" )
  async def endSC( self, ctx ):
    """
    Must have a skill challenge already active.

    Ends the current skill challenge tracking, outputting the current
    status back to the user and reseting internal variables.
    """
    await self.bot.wait_until_ready()

    if not self.activeSC: 
      await self.displayNoActiveSCError( ctx )
      return 

    await ctx.send("The skill challenge has been ended abruptly!")

    await self.displaySCStats()
    
    self.resetSCVars()

    pass

  ##############################################
  # Support Functions 
  ##############################################
  async def checkDuplicateCounts( self, ctx ):
    """
    Checks the initiative count list to ensure there 
    are no duplicates, and handles duplicates by creating
    'decimal initiative'. 
    """
    # Support function to make sure input is correct 
    def check(msg):
      return msg.content == "1" or msg.content == "2"

    noConflicts = False 
    conflict = False
    # While there are stil lconflicts in the list 
    while not noConflicts:
      totalCreatures = len(self.initOrder)

      conflict = False # used to make sure we need to check again
      # Loop through the whole list 
      for i in range(0, totalCreatures):
        # if we're not at the end
        if i != totalCreatures - 1:

          creature = self.initOrder[i]
          nextCreature = self.initOrder[i+1]
          # if these creatures have the same initiative count
          if creature.initCount == nextCreature.initCount:
            conflict = True

            # Display the conflicting creatures
            messageStr = f"WARNING: One or more creatures has the same initiative count '{creature.initCount}':\n"
            messageStr += f"1. {creature.name}\n"
            messageStr += f"2. {nextCreature.name}\n"
            messageStr += "Which creature would you like to go first (1 or 2)?"

            # check for user input that is within given constraints
            await ctx.send(messageStr)
            msg = await self.bot.wait_for("message", check=check)

            # turn the creature's initiative count into a string
            initStr = str(math.floor(creature.initCount))
            # add the string to the conflicts list
            if initStr in self.conflicts:
              self.conflicts[initStr] += 1
            else:
              self.conflicts[initStr] = 1

            # Calculate the new count based on how many conflicts:
            # 1 conflict = 0.5, 2 = 0.25, etc. The decimal is added to the initiative count
            # in order to resolve the conflict while still maintaining order
            newCount = creature.initCount + 1 / (2 * self.conflicts[initStr])
            newCount = round(newCount, 3)

            if msg.content == "1":
              creature.initCount = newCount
              await ctx.send(f"Alright! Creature '{creature.name}' has been updated with an initiative count of '{creature.initCount}'.")
            elif msg.content == "2":
              nextCreature.initCount = newCount
              await ctx.send(f"Alright! Creature '{nextCreature.name}' has been updated with an initiative count of '{nextCreature.initCount}'.")
            break
          # We keep looping until there are guaranteed no conflicts
          elif i + 1 == totalCreatures - 1 and not conflict:
            noConflicts = True
      # re-sort the initiative order to make sure everything is correct
      self.sortInitOrder()

    return
  
  async def displayActiveSCError( self, ctx):
    """
    Shows an error regarding already having a current active skill challenge.
    """
    await ctx.send("ERROR: There is already an active skill challenge. Please end the active challenge by using the '!sc end' command.")
    return 

  async def displayNoActiveSCError( self, ctx ):
    """
    Shows an error regarding not having a current active skill challenge.
    """
    await ctx.send("ERROR: There is not currently an active skill challenge. Please start a skill challenge using '!sc start' before using this command.")
    return 

  async def displaySCStats( self, ctx ):
    """
    Displays a markdown code block of all the information the Traveler is currently storing
    regarding the current skill challenge. 
    """

    displayStr = "```md\n# Skill Challenge Information:\n"
    # Current Status
    # - Successes / Success Limit
    displayStr += f"<S>: Successes:  {self.successes} / {self.successLimit} to win\n"
    # - Failures / Fail Limit
    displayStr += f"[F]: Failures:   {self.fails} / 3 to lose\n\n"
    
    displayStr += "General Data:\n====================\n"

    # Show stats for the encounter
    # - Difficulty Setting
    # - DC to Beat
    displayStr += " - Tier: "
    tier = self.tierData.tier
    if tier == 1:
      displayStr += TIER_1_STR
    elif tier == 2:
      displayStr += TIER_2_STR
    elif tier == 3:
      displayStr += TIER_3_STR
    elif tier == 4:
      displayStr += TIER_4_STR

    displayStr += "\n - Difficulty: "
    difficulty = self.tierData.difficulty
    if difficulty == 1:
      displayStr += "Easy"
    elif difficulty == 2:
      displayStr += "Medium"
    elif difficulty == 3:
      displayStr += "Hard"

    skillDC = self.tierData.skillDC
    displayStr += f" | DC: {skillDC}"

    spellSuccessLevel = self.tierData.spellSuccessLevel
    if spellSuccessLevel == 1:
      spellPlaceStr = "st"
    elif spellSuccessLevel == 2:
      spellPlaceStr = "nd"
    elif spellSuccessLevel == 3:
      spellPlaceStr = "rd"
    else:
      spellPlaceStr = "th"
    displayStr += f" | Spell Success: {spellSuccessLevel}{spellPlaceStr}-lvl\n\n"

    # Loop through locked skills 
    if not self.checkActionListsEmpty():
      displayStr += "Locked Skills:\n====================\n"
    # - Attacks
    
    if len(self.lockedAttacks) > 0:
      displayStr += " - Attacks:\n   > "
      for action in self.lockedAttacks:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:len(self.lockedAttacks) - 2]
    # else:
    # displayStr += "NONE\n"
    # - Items
    if len(self.lockedItems) > 0:
      displayStr += " - Items:\n   > "
      for action in self.lockedItems:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:len(self.lockedItems) - 2]
    # else:
      # displayStr += "NONE\n"
    # - Skills
    if len(self.lockedSkills) > 0:
      displayStr += " - Skills:\n   > "
      for action in self.lockedSkills:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:len(self.lockedSkills) - 2]
    # else:
      # displayStr += "NONE\n"
    # - Spells
    if len(self.lockedSpells) > 0:
      displayStr += " - Spells:\n   > "
      for action in self.lockedSpells:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:len(self.lockedSpells) - 2]
    # else:
      # displayStr += "NONE\n"
    # - Other Actions
    if len(self.lockedOther) > 0:
      displayStr += " - Other Actions:\n   > "
      for action in self.lockedOther:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:len(self.lockedOther) - 2]
    # else:
      # displayStr += "NONE\n"

    if not self.checkActionListsEmpty():
      displayStr += "\n"

    # Show initiative order
    if len(self.initOrder) > 0:
      displayStr += "Initiative Order:\n====================\n"
      for creature in self.initOrder:
        if creature.creatureType == SC_CreatureType.ALLY:
          displayStr += "<A>: "
        elif creature.creatureType == SC_CreatureType.COMPLICATION:
          displayStr += "[C]: "
        elif creature.creatureType == SC_CreatureType.ENEMY:
          displayStr += "[E]: "
        else:
          displayStr += "{P}: "
        displayStr += f" ({creature.initCount}) - {creature.name}\n"

    displayStr +="```"

    return await ctx.send( displayStr )

  async def getInitOrder( self , ctx ):
    """
    Helper Function for '!sc start' command.
    Handles the collecting of initiative until the typing
    of done is completed.
    """
    async def checkMsg( ctx, msg ):
      """
      Helper function for '!s init start' command.

      Assists with determining whether or not message is 
      properly formatted / has relevant data to add to the initiative order.
      """
      content = msg.content
      channel = msg.channel
      try:

        # If the channel is different than the starting channel for initiative
        if channel != self.initChannel:
          return True
        # If someone indicates we're finished
        elif content == "done":
          return False

        # if creature is designated an ally
        if "ALLY" in content:
          content = content.replace("ALLY", "")
          ctype = SC_CreatureType.ALLY
        # if creature is designated an enemy
        elif "ENEMY" in content:
          content = content.replace("ENEMY", "")
          ctype = SC_CreatureType.ENEMY
        # otherwise, it must be a player
        elif "COMPLICATION" in content:
          content = content.replace("COMPLICATION", "")
          ctype = SC_CreatureType.COMPLICATION
        else:
          ctype = SC_CreatureType.PLAYER
          
        # parse the number from the message
        numbers = [int(word) for word in content.split() if word.isdigit()]
        # get the rest of the message
        words = [word for word in content.split() if not word.isdigit()]
        
        # Combine the words together into the creature's name
        name = ""
        wordCount = 0
        for word in words:
          if wordCount > 0:
            name += " "
          name += word
          wordCount += 1
          
        # get the initiative count from numbers
        initCount = numbers[0]
        # Add the creature to the initiative count
        newCreature = SC_Creature( name, initCount , ctype )
        self.initOrder.append( newCreature )
        # let the user know the creature was successfully added
        await ctx.send(f"Creature '{name}' with initiative count '{initCount}' added!")
        return True  
      # Something was not right about the creature
      except:
        await ctx.send("Huh. That doesn't look right. Try sending it again in the following format. ```<name> <roll> OR <roll> <name>\nExample: 'Flint 13' OR '13 Flint'```")
        return True

    # Collect initiative 
    collectInitiative = True 
    while collectInitiative:
      msg = await self.bot.wait_for("message")
      collectInitiative = await checkMsg( ctx, msg )

    # Sort the list
    self.sortInitOrder()
    # Check if there are duplicate initiative counts
    await self.checkDuplicateCounts( ctx )

    await ctx.send("----------")
    await ctx.send("Initiative Order collected!")

    return 

  def addActionToLst( self, action ):
    """
    Adds a given SC_LockableSkill type object to the list containing objects of its type. 
    """
    if action.actionType == SC_ActionType.ATTACK:
      self.lockedAttacks.append(action)
      self.lockedAttacks.sort( key = lambda x: x.name, reverse = True )
    elif action.actionType == SC_ActionType.ITEM:
      self.lockedItems.append(action)
      self.lockedItems.sort( key = lambda x: x.name, reverse = True )
    elif action.actionType == SC_ActionType.SKILL:
      self.lockedSkills.append(action)
      self.lockedSkills.sort( key = lambda x: x.name, reverse = True )
    elif action.actionType == SC_ActionType.SPELL:
      self.lockedSpells.append(action)
      self.lockedSpells.sort( key = lambda x: x.name, reverse = True )
    elif action.actionType == SC_ActionType.OTHER:
      self.lockedOther.append(action)
      self.lockedOther.sort( key = lambda x: x.name, reverse = True )
    return

  def checkActionListsEmpty( self ):
    """
    Checks to make sure all the action lists are empty. Used to streamline display for '!sc display'
    """
    if len(self.lockedAttacks) > 0:
      return False 
    elif len(self.lockedItems) > 0:
      return False 
    elif len(self.lockedSkills) > 0:
      return False
    elif len(self.lockedSpells) > 0:
      return False 
    elif len(self.lockedOther) > 0:
      return False 
    return True

  def resetSCVars( self ):
    """
    Resets all challenge-specific variables to their default
    setting (i.e. before a skill challenge has been initiated)
    """
    self.activeSC = False 
    self.fails = 0
    self.successes = 0
    self.successLimit = 0
    self.initChannel = None
    self.initOrder = []
    self.lockedAttacks = []
    self.lockedItems = []
    self.lockedSkills = []
    self.lockedSpells = []
    self.lockedOther = []
    return

  def sortInitOrder( self ):
    self.initOrder.sort( key = lambda x: x.initCount, reverse = True )
    return 

##############################################
# Setup Function for SkillChallenge Cog
##############################################
def setup( bot ):
  print("Attempting load of 'skillchallenge' extension...")
  bot.add_cog( SkillChallenge( bot ) )