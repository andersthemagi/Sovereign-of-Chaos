##############################################
# Package Imports
##############################################

import enum
import re

from discord import Message
from discord.ext.commands import Bot, Context

from init_classes import InitInstance

##############################################
# Constants, Classes, and Setup
##############################################

# Complication Modifiers
# As a 'complication' in a skill challenge, the creature
# has a set modifier to their roll. Depending on difficulty this
# modifier can be higher or lower.

COMPLICATION_MOD_EASY = 2
COMPLICATION_MOD_MODERATE = 4
COMPLICATION_MOD_HARD = 6
COMPLICATION_MOD_DAUNTING = 8
COMPLICATION_MOD_FORMIDABLE = 10

# DCs
# Sets the minimum a player needs to roll total in order to succeed
EASY_DC = 10
MODERATE_DC = 15
HARD_DC = 20

# Display Strings for Tier of Play
TIER_1_STR = "Local Heroes (1-4th level)"
TIER_2_STR = "Heroes of the Realm (5-9th level)"
TIER_3_STR = "Masters of the Realm (10-14th level)"
TIER_4_STR = "Masters of the World (15-20th+ level)"

AFFIRMATIVES = [
  "y", "yes", "yep", "yeah", "definitely", "fuck yes"
]
NEGATIVES = [
  "n", "no", "nope", "nah", "not at all", "fuck no"
]

# Dictionary for easily storing data for developing
# skills challenges quickly
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

# SC_CreatureType class
# Used as a method of comparing / confirming creature type
class SC_CreatureType(enum.Enum):
  ALLY = 1,
  COMPLICATION = 2,
  ENEMY = 3,
  PLAYER = 4

# SC_Creature class
# Represents a creature in the skill challenge
class SC_Creature:

  def __init__(self, name: str, initCount: int, creatureType: SC_CreatureType = SC_CreatureType.PLAYER ):
    self.name = name 
    self.initCount = initCount
    self.creatureType = creatureType
    return 

# SC_ActionType class
# Classifies skills into one of five types
class SC_ActionType(enum.Enum):
  ATTACK = 1,
  ITEM = 2,
  SKILL = 3,
  SPELL = 4,
  OTHER = 5

# SC_LockableSkill class
# Represents a skill used by a creature in the skill challenge
class SC_LockableSkill:

  def __init__( self, name: str, action_type: SC_ActionType = SC_ActionType.SKILL ):
    self.name = name 
    self.actionType = action_type
    return

# SC_TierData
# Template class for allowing easy building of skill challenges
class SC_TierData:

  def __init__( self, name: str, comp_mod: int, tier: int, difficulty: int ):
    self.name = name
    self.compMod = comp_mod
    self.difficulty = difficulty 
    self.tier = tier 
    self.setTierVars()
    return

  def setTierVars( self ) -> None:
    varData = tierData[self.tier]
    self.spellSuccessLevel = varData["spellSuccessLevel"]
    self.skillDC = varData[self.difficulty]["skillDC"]
    self.successLimit = varData[self.difficulty]["successLimit"]
    return

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

VALID_ACTIONS = [
  "attack","item", "skill", "spell", "other"
]

##############################################
# SC_Instance Class
##############################################

class SC_Instance( InitInstance ):

  def __init__( self, bot: Bot ):
    super().__init__( bot )
    self.failLimit = 3
    self.reset()
    return

  ##############################################
  # SC_Instance External Commands
  ##############################################  

  async def start( self, ctx: Context ) -> None:
    """
    Starts a skill challenge in the given channel
    """
    if self.activeSC:
      await self.displayActiveSCError( ctx )
      return 

    # Set channel 
    self.initChannel = ctx.message.channel

    # Choose a tier of play
    displayStr = f"```md\n1. {TIER_1_STR}\n2. {TIER_2_STR}\n"
    displayStr += f"3. {TIER_3_STR}\n4. {TIER_4_STR}\n```"
    await ctx.send(displayStr)
    await ctx.send("Which tier of play would you like to use (1-4)? Type 'nvm' to exit.")
    collectingTier = True 
    while collectingTier:
      msg = await self.bot.wait_for("message")
      if msg.content == "nvm":
        await ctx.send("Exiting skill challenge creation.")
        self.reset()
        return
      collectingTier, tier = await self.checkForValidTier( ctx, msg )

    # Choose a difficulty setting
    displayStr = f"```md\n1. Easy\n2. Medium\n3. Hard\n```"
    await ctx.send(displayStr)
    await ctx.send("What difficulty will this challenge be (1-3)? Type 'nvm' to exit")
    collectingDifficulty = True 
    while collectingDifficulty:
      msg = await self.bot.wait_for("message")
      if msg.content == "nvm":
        await ctx.send("Exiting skill challenge creation.")
        self.reset()
        return
      collectingDifficulty, difficulty = await self.checkForValidDifficulty( ctx, msg )

    presetStr = f"SC_TIER{tier}_D{difficulty}"
    self.tierData = globals()[presetStr]
    self.skillDC = self.tierData.skillDC
    self.successLimit = self.tierData.successLimit

    # Collect initiative order
    await ctx.send("----------")
    await self.displayRandStartQuip( ctx )
    await ctx.send("----------")
    await ctx.send("Accepting input for characters!\n\nPlease type in '<name> <roll>' into the chat and I'll make a note of it. Example ```'Flint 13' OR\n'13 Flint' OR\n'Diva 13 Thiccums'```")
    await ctx.send("----------")
    await self.getInitOrder( ctx )

    self.activeSC = True
    self.activeInitiative = True

    await self.displaySCStats( ctx )

    # Display order + used skills to the users
    
    return 

  async def end( self, ctx: Context ) -> None:
    """
    Ends a skill challenge in the given channel.
    """
    await ctx.send("----------")
    await ctx.send("Skill challenge has been ended abruptly! Here are the current results")

    await self.displaySCStats( ctx )

    self.reset()
    return

  async def addAction( self, ctx: Context ) -> None:
    """
    Adds a completed skill challenge action to the order. Handles
    win conditions and typing as well
    """
    
    displayStr = "```md\nAction Types:\n====================\n"
    for action in VALID_ACTIONS:
      displayStr += f"- {action.capitalize()}\n"
    displayStr += "```"

    await ctx.send(displayStr)
    await ctx.send("What kind of action would you like to add? **Type one of the kinds of actions above** and I'll walk you through the rest. Otherwise, type 'nvm' to exit this menu.")
    
    gettingType = True
    while gettingType:
      msg = await self.bot.wait_for("message")
      if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
      actionType, gettingType = await self.checkMsgForActionType( ctx, msg )

    # - Resolve based on what type of action it is
    if actionType == "attack":
      await self.resolveSCAttack( ctx )
    elif actionType == "item":
      await self.resolveSCItem( ctx )
    elif actionType == "skill":
      await self.resolveSCSkill( ctx )
    elif actionType == "spell":
      await self.resolveSCSpell( ctx )
    elif actionType == "other":
      await self.resolveSCOther( ctx )

    # Resolve success / failure
    await self.checkWinCon( ctx )

    # Display current status to the party
    await self.displaySCStats( ctx )

    return

  async def addInitCreature( self, ctx: Context ) -> None:

    await ctx.send("----------")
    await ctx.send("Accepting input for characters!\n\nPlease type in '<name> <roll>' into the chat and I'll make a note of it. Example ```'Flint 13' OR\n'13 Flint' OR\n'Diva 13 Thiccums'```")
    await ctx.send("----------")
    await self.getInitOrder( ctx )

    await self.displaySCStats( ctx )

    return 

  async def editInitCreature( self, ctx: Context ) -> None: 
    """
    Wrapper for super class function editCreatures(). Allows the user 
    to change the initiative order of a creature.
    """
    await self.editCreatures( ctx )
    return

  async def removeInitCreature( self, ctx: Context ) -> None:
    """
    Wrapper for super class function removeCreatures(). Allows the user 
    to remove a creature from the initiative order.
    """
    await self.removeCreatures( ctx )
    return 

  async def shuffleInitCreatures( self, ctx: Context ) -> None:
    """
    Wrapper for super class function suffleCreatures(). Allows the user to shuffle the initiative order.
    """
    await self.shuffleInitOrder( ctx )
    return

  ##############################################
  # SC_Instance Internal Functions
  ##############################################

  # ASYNC SUPPORT FUNCTIONS

  async def checkForValidDifficulty( self, ctx: Context, msg: Message ) -> (int, bool):
    """
    Support function for '!sc start' command. Checks whether a given integer represents a valid difficulty setting. 
    """
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

  async def checkForValidTier( self, ctx: Context, msg: Message ) -> (int, bool):
    """
    Support function for '!sc start' command. Checks whether a given integer represents a valid tier of gameplay.
    """
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
  
  async def checkMsg( self, ctx: Context , msg: Message ) -> bool:
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
      numbers = [int(word) for word in re.findall(r'-?\d+', content)]
      for word in re.findall(r'-?\d+', content):
        content = content.replace(word, "")
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

  async def checkMsgForActionType( self, ctx: Context, msg: Message ) -> (str, bool):
    """
    Support function for '!sc add' command. Checks whether a given string contains a valid option for action collection.
    """
    actionType = None
    content = msg.content.lower()
    if content in VALID_ACTIONS:
      actionType = content
      return actionType, False
    else:
      await ctx.send("That's not a type I recognize. Take a look at the list above and choose one from there.")
      return actionType, True 

  async def checkValidYNResponse( self , ctx: Context , inStr: str ) -> bool:
    """
    Support function for '!sc add' command. Used to check whether a valid yes/no response has been received. 
    """
    if inStr in AFFIRMATIVES:
      await ctx.send("Wonderful! I've added a success to your count then.")
      self.successes += 1
      return False 
    elif inStr in NEGATIVES:
      await ctx.send("I see. There's always next time, I suppose. A failure has been added to your count.")
      self.fails += 1
      return False 
    else:
      await ctx.send("I couldn't recognize whether that was an affirmative or negative response. Try using one of the examples below:")
      displayStr = "```md\nAffirmatives: "
      for word in AFFIRMATIVES:
        displayStr += f"{word}, "
      displayStr = displayStr[:-2] + "\n"
      displayStr += "Negatives: "
      for word in NEGATIVES:
        displayStr += f"{word}, "
      displayStr = displayStr[:-2]
      displayStr += "\n```"
      await ctx.send(displayStr)
      return True 

  async def checkWinCon( self, ctx: Context ) -> None:
    """
    Support function for '!sc add' function. Checks whether a win condition has been met for the skill challenge.
    """
    if self.successes >= self.successLimit:
      await ctx.send("Great success! You've won this skill challenge, this time around.")
      await self.end( ctx )
      return

    elif self.fails >= 3:
      await ctx.send("You have failed this skill challenge. Sad!")
      await self.end( ctx )
      return 

    return    
  
  async def displayActiveSCError( self, ctx: Context ) -> None:
    """
    Shows an error regarding already having a current active skill challenge.
    """
    await ctx.send("ERROR: There is already an active skill challenge. Please end the active challenge by using the '!sc end' command.")
    return 

  async def displayNoActiveSCError( self, ctx: Context ) -> None:
    """
    Shows an error regarding not having a current active skill challenge.
    """
    await ctx.send("ERROR: There is not currently an active skill challenge. Please start a skill challenge using '!sc start' before using this command.")
    return 

  async def displayInitOrder( self, ctx: Context ) -> None:
    """
    Rewrite of displayInitOrder in InitInstance class. Sets the display
    to show SC stats instead of just initiative order.
    """
    await self.displaySCStats( ctx )
    return

  async def displaySCStats( self, ctx: Context ) -> None:
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
      displayStr += "Locked Actions:\n====================\n"
    # - Attacks
    
    if len(self.lockedAttacks) > 0:
      displayStr += " - Attacks: "
      for action in self.lockedAttacks:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:-2]
      displayStr += "\n"
    # else:
    # displayStr += "NONE\n"
    # - Items
    if len(self.lockedItems) > 0:
      displayStr += " - Items: "
      for action in self.lockedItems:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:-2]
      displayStr += "\n"
    # else:
      # displayStr += "NONE\n"
    # - Skills
    if len(self.lockedSkills) > 0:
      displayStr += " - Skills: "
      for action in self.lockedSkills:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:-2]
      displayStr += "\n"
    # else:
      # displayStr += "NONE\n"
    # - Spells
    if len(self.lockedSpells) > 0:
      displayStr += " - Spells: "
      for action in self.lockedSpells:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:-2]
      displayStr += "\n"
    # else:
      # displayStr += "NONE\n"
    # - Other Actions
    if len(self.lockedOther) > 0:
      displayStr += " - Other Actions: "
      for action in self.lockedOther:
        displayStr += f"{action.name}, "
      displayStr = displayStr[:-2]
      displayStr += "\n"
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

    # Show removed creatures
    if len(self.removedCreatures) > 0:
      displayStr += "Removed Creatures:\n====================\n"
      for creature in self.removedCreatures:
        displayStr += "> "
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

    await ctx.send( displayStr )
    return 

  async def resolveSCAttack( self, ctx: Context ) -> None:
    """
    Support function for '!sc add' command. Resolves the addition of an executed attack to the skill challenge
    """
    # Who made the roll?
    await ctx.send("Ah an attack was made. Who made said attack? Type 'nvm' at any point to cancel this process.")
    msg = await self.bot.wait_for("message")
    if msg.content == 'nvm':
      await ctx.send("Sounds good! Cancelling.")
      return 
    creatureName = msg.content

    # Name of attack
    await ctx.send(f"So {creatureName} made an attack? With what, exactly?")
    msg = await self.bot.wait_for("message")
    if msg.content == 'nvm':
      await ctx.send("Sounds good! Cancelling.")
      return 
    tool = msg.content
      
    if self.checkForStartVowel( tool ):
      indefArticle = "an"
    else:
      indefArticle = "a"

    await ctx.send(f"{creatureName} attacked with {indefArticle} {tool}, then. Did they manage to hit?")

    # Output success / failure
    collectingResponse = True
    while collectingResponse:
      msg = await self.bot.wait_for("message")
      content = msg.content.lower()
      if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
      collectingResponse = await self.checkValidYNResponse( ctx , content )
      
    # Add skill to the list
    skillName = f"{tool}[{creatureName}]"
    newAction = SC_LockableSkill( skillName, SC_ActionType.ATTACK )
    self.addActionToLst( newAction )

    return

  async def resolveSCItem( self, ctx: Context ) -> None:
    """
    Support function for '!sc add' command. Resolves the addition of a used item to the skill challenge
    """
    # Name of item?
    await ctx.send("Okay an item was used, I can work with that. Who used that item?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
    creatureName = msg.content

    await ctx.send(f"So {creatureName} used an item? What was it?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
    item = msg.content

    if self.checkForStartVowel( item ):
      indefArticle = "an"
    else:
      indefArticle = "a"

    # Did it succeed?
    await ctx.send(f"{creatureName} used {indefArticle} {item}, got it. Did the item work?")

    # Output success / failure
    collectingResponse = True
    while collectingResponse:
      msg = await self.bot.wait_for("message")
      if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
      content = msg.content.lower()
      collectingResponse = await self.checkValidYNResponse( ctx, content )
      
    skillName = f"{item}[{creatureName}]"
    newAction = SC_LockableSkill( skillName, SC_ActionType.ITEM )
    self.addActionToLst( newAction )

    return 

  async def resolveSCOther( self, ctx: Context ) -> None:
    """
    Support function for '!sc add' command. Resolves the addition of an action to the skill challenge that doesn't already have a category.
    """
    # Name of creature
    await ctx.send("So you don't really have an idea what ***kind*** of thing just happened. Fair enough, to be honest with you. Who performed the action?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
    creatureName = msg.content

    # Name of action
    await ctx.send(f"Okay, so {creatureName} did it. What did they do?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
    actionName = msg.content 

    await ctx.send(f"{creatureName} did '{actionName}'. Interesting. Did it succeed even?")

    collectingResponse = True
    while collectingResponse:
      msg = await self.bot.wait_for("message")
      if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
      content = msg.content.lower()
      collectingResponse = await self.checkValidYNResponse( ctx, content )
      
    skillName = f"{actionName}[{creatureName}]"
    newAction = SC_LockableSkill( skillName, SC_ActionType.OTHER )
    self.addActionToLst( newAction )

    return

  async def resolveSCSkill( self, ctx: Context ) -> None:
    """
    Support function for '!sc add' command. Resolves the addition of a used skill to the skill challenge
    """
    # Who used the skill?
    await ctx.send("A skill was used! Who used it?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
    creatureName = msg.content 

    # Name of skill?
    await ctx.send(f"Which skill did {creatureName} use?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
    skillName = msg.content 

    # Roll?
    await ctx.send(f"What did {creatureName} roll for '{skillName}'?")
    collectingRoll = True 
    while collectingRoll:
      try:
        msg = await self.bot.wait_for("message")
        if msg.content == "nvm":
          await ctx.send("Sounds good! Cancelling.")
          return
        roll = int(msg.content)
        collectingRoll = False 
      except:
        await ctx.send("I don't think that was something I could use as a number. Try to type in a number like `1` or `-200` or something.")

    lockableName = f"{skillName}[{creatureName}]"
    newAction = SC_LockableSkill( lockableName, SC_ActionType.SKILL )
    self.addActionToLst( newAction )
    
    # Check roll against DC
    if roll < self.skillDC:
      await ctx.send(f"A **{roll}** does not succeed on a **DC {self.skillDC}** check. One (1) failure for the party with debatable morals!")
      self.fails += 1
    else:
      await ctx.send(f"A **{roll}** beats or meets a **{self.skillDC}**! I'll add a success to your current challenge.")
      self.successes += 1

    return 

  async def resolveSCSpell( self, ctx: Context ) -> None:
    """
    Support function for '!sc add' command. Resolves the addition of a cast spell to the skill challenge
    """
    # Who cast the spell?
    await ctx.send("Might ***AND*** Magic! Who used that spell?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
    creatureName = msg.content

    # Name of spell?
    await ctx.send(f"What spell did {creatureName} use?")
    msg = await self.bot.wait_for("message")
    if msg.content == "nvm":
      await ctx.send("Sounds good! Cancelling.")
      return
    spellName = msg.content

    # Level of spell?
    collectingLvl = True
    await ctx.send(f"What level spell is {spellName}?")
    while collectingLvl:
      try:
        msg = await self.bot.wait_for("message")
        if msg.content == "nvm":
          await ctx.send("Sounds good! Cancelling.")
          return
        spellLvl = int(msg.content)
        collectingLvl = False
      except:
        await ctx.send("I don't think that was a number. Please try with a valid number. ")

    if spellLvl == 0:
      suffix = "th"
    if spellLvl == 1:
      suffix = "st"
    elif spellLvl == 2:
      suffix = "nd"
    elif spellLvl == 3:
      suffix = "rd"
    else:
      suffix = "th"

    # Did it succeed?
    displayStr = f"Great! So {creatureName} cast {spellName} at {spellLvl}{suffix}-lvl "
    if spellLvl == 0:
      displayStr += "(cantrip)"
    displayStr += f". Did it succeed?"
    await ctx.send(displayStr)
    
    collectingResponse = True
    while collectingResponse:
      msg = await self.bot.wait_for("message")
      if msg.content == "nvm":
        await ctx.send("Sounds good! Cancelling.")
        return
      content = msg.content.lower()
      collectingResponse = await self.checkValidYNResponse( ctx, content )
      
    lockableName = f"{spellName}({spellLvl})[{creatureName}]"
    newAction = SC_LockableSkill( lockableName, SC_ActionType.SPELL )
    self.addActionToLst( newAction )
    # output success / failure

    return

  # SYNCHRONOUS SUPPORT FUNCTIONS

  def addActionToLst( self, action: SC_LockableSkill ) -> None:
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

  def checkActionListsEmpty( self ) -> bool:
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

  def checkActiveSC( self ) -> bool:
    return self.activeSC

  def checkForStartVowel( self, inStr: str ) -> bool:
    """
    Checks whether a given string starts with a vowel. 
    """
    checkStr = inStr.lower()
    vowels = ["a", "e", "i", "o", "u"]

    for vowel in vowels:
      if checkStr.startswith(vowel):
        return True 

    return False

  def reset( self ) -> None:
    """
    Resets all challenge-specific variables to their default
    setting (i.e. before a skill challenge has been initiated)
    """
    self.activeSC = False 
    self.activeInitiative = False 
    self.fails = 0
    self.initChannel = None
    self.skillDC = 0
    self.successes = 0
    self.successLimit = 0
    
    self.conflicts = {}
    self.initOrder = []
    self.lockedAttacks = []
    self.lockedItems = []
    self.lockedSkills = []
    self.lockedSpells = []
    self.lockedOther = []
    self.removedCreatures = []
    return
  
  # End of SC_Instance class

# End of File
