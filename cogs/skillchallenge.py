##############################################
# Package Imports
##############################################
import enum
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

    # TODO: Implement !sc start command

    await self.bot.wait_until_ready()

    if self.activeSC:
      await self.displayNoActiveSCError( ctx )
      return 

    self.tierData = SC_TIER1_D1
    self.successLimit = self.tierData.successLimit

    # Choose a tier of play
    # collectingTier = True 
    # while collectingTier:
      # pass

    # Choose a difficulty setting
    # collectingDifficulty = True 
    # while collectingDifficulty:
      # pass

    # Collect initiative order 

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

    # TODO: Implement !sc end command

    await self.bot.wait_until_ready()

    if not self.activeSC: 
      await self.displayNoActiveSCError( ctx )
      return 

    
    self.resetSCVars()

    pass

  ##############################################
  # Support Functions 
  ##############################################
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
    self.initOrder = []
    self.lockedAttacks = []
    self.lockedItems = []
    self.lockedSkills = []
    self.lockedSpells = []
    self.lockedOther = []
    return

##############################################
# Setup Function for SkillChallenge Cog
##############################################
def setup( bot ):
  print("Attempting load of 'skillchallenge' extension...")
  bot.add_cog( SkillChallenge( bot ) )