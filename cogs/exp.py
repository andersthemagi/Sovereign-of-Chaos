##############################################
# Package Imports
##############################################
import asyncio
import discord 
import time
import re

from datetime import datetime, timedelta
from discord import Guild, Message, Member, RawReactionActionEvent
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

import database
from log import ConsoleLog

##############################################
# Constants
##############################################

MODULE = "EXP"

REACT_ROLE_MSG_IDS = [
  "882013329411948606"
]

BASIC_XP_ROLES = [
  "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", 
  "Level 6", "Level 7", "Level 8", "Level 9", "Level 10"
]

CLASS_ROLES = [
  "Bard", "Cleric", "Fighter", "Mage",
  "Paladin", "Ranger", "Rogue", "Warlock"
]

BARD_XP_ROLES = [
  "Lyrist (LVL 1)", "Ryymer (LVL 2)", "Sonateer (LVL 3)",
  "Skald (LVL 4)", "Racaraide (LVL 5)", "Joungleur (LVL 6)",
  "Troubadour (LVL 7)", "Minstrel (LVL 8)", "Lorist (LVL 9)",
  "Master Lorist (LVL 10)"
]

CLERIC_XP_ROLES = [
  "Aspirant (LVL 1)", "Acolyte (LVL 2)", "Adept (LVL 3)", "Vicar (LVL 4)",
  "Curate (LVL 5)", "Deacon (LVL 6)", "Priest (LVL 7)", "Abbot (LVL 8)",
  "Bishop (LVL 9)", "Archbishop (LVL 10)"
]

FIGHTER_XP_ROLES = [
  "Warrior (LVL 1)", "Veteran (LVL 2)", "Swordmaster (LVL 3)",
  "Crusader (LVL 4)", "Swashbuckler (LVL 5)", "Myrmidon (LVL 6)",
  "Sentinel (LVL 7)", "Champion (LVL 8)", "Lord (LVL 9)",
  "High Lord (LVL 10)"
]

MAGE_XP_ROLES = [
  "Prestidigitator (LVL 1)", "Magician (LVL 2)", "Conjurer (LVL 3)",
  "Theurgist (LVL 4)", "Evoker (LVL 5)", "Seer (LVL 6)", 
  "Enchanter / Enchantress (LVL 7)", 
  "Senior Enchanter / Enchantress (LVL 8)",
  "First Enchanter / Enchantress (LVL 9)",
  "Grand Enchanter / Enchantress (LVL 10)"
]

PALADIN_XP_ROLES = [
  "Recruit (LVL 1)", "Templar (LVL 2)", "Knight-Private (LVL 3)",
  "Knight-Corporal (LVL 4)", "Knight-Sergeant (LVL 5)",
  "Knight-Lieutenant (LVL 6)", "Knight-Captain (LVL 7)",
  "Knight-Commander (LVL 8)", "Knight-Vigilant (LVL 9)",
  "Knight-Divine (LVL 10)"
]

RANGER_XP_ROLES = [
  "Runner (LVL 1)", "Strider (LVL 2)", "Scout (LVL 3)",
  "Courser (LVL 4)", "Tracker (LVL 5)", "Hinterlander (LVL 6)",
  "Pathfinder (LVL 7)", "Ranger (LVL 8)", "Senior Ranger (LVL 9)",
  "Master Ranger (LVL 10)"
]

ROGUE_XP_ROLES = [
  "Apprentice (LVL 1)", "Footpad (LVL 2)", "Burglar (LVL 3)",
  "Thug (LVL 4)", "Sharper (LVL 5)", "Pilferer (LVL 6)",
  "Swindler (LVL 7)", "Trickster (LVL 8)", "Thief (LVL 9)",
  "Master Thief (LVL 10)"
]

WARLOCK_XP_ROLES = [
  "Neophyte (LVL 1)", "Occultist (LVL 2)", "Invoker (LVL 3)",
  "Mystic (LVL 4)", "Hexer (LVL 5)", "Warlock / Witch (LVL 6)",
  "Pact Master (LVL 7)" , "Soulbinder (LVL 8)", "Magister (LVL 9)",
  "Archon (LVL 10)"
]

ROLE_LISTS = [
  BASIC_XP_ROLES, CLASS_ROLES, BARD_XP_ROLES, CLERIC_XP_ROLES, 
  FIGHTER_XP_ROLES, MAGE_XP_ROLES, PALADIN_XP_ROLES, RANGER_XP_ROLES, 
  ROGUE_XP_ROLES, WARLOCK_XP_ROLES
]

ADJUST_LVLS_GET_SCRIPT = """
SELECT user_id, xp, lvl FROM users;
"""

ADJUST_LVLS_SET_SCRIPT = """
UPDATE users SET lvl = %s WHERE user_id = %s;
"""

ASSIGN_XP_GET_SCRIPT = """
SELECT class_name FROM users WHERE user_id = %s;
"""

ASSIGN_XP_SET_SCRIPT = """
UPDATE users SET rank_name = %s WHERE user_id = %s;
"""

LEADERBOARD_SCRIPT = """
SELECT user_id, xp, lvl FROM users ORDER BY xp DESC LIMIT 10;
"""

CHECK_PROG_SCRIPT = """
SELECT class_name, xp, lvl FROM users WHERE user_id = %s;
"""

CHECK_RANK_SCRIPT = """
SELECT user_id, xp, lvl, class_name, rank_name FROM users WHERE user_id = %s;
"""

CHECK_USER_EXISTS_SCRIPT = """SELECT * FROM users WHERE user_id = %s;"""

RESET_DAILY_STREAK_SCRIPT = """
UPDATE users SET daily_xp_streak = 0 WHERE messaged_today = False;
"""

RESET_DAILY_XP_SCRIPT = """
UPDATE users SET daily_xp_earned = False;
"""

RESET_MESSAGED_TODAY_SCRIPT = """
UPDATE users SET messaged_today = False;
"""

UPDATE_USER_CLASS_SCRIPT = """
UPDATE users SET class_name = %s WHERE user_id = %s;
"""

##############################################
# EXP Cog
##############################################

class Exp( commands.Cog, name = "Exp" ):

  def __init__( self, bot: Bot ):
    self.bot = bot 
    self.db = database.DB()
    self.doubleXP = False
    self.logging = ConsoleLog()

  ##############################################
  # EXP Cog Async Tasks
  ##############################################

  @tasks.loop( hours = 24 ) 
  async def resetDailyXPBonus( self ) -> None:
    """
    Resets the daily xp bonus flags to allow players to earn bonus xp again.
    """
    self.db.start()
    self.logging.send( MODULE, "Resetting daily xp flags." )
    self.db.executeScript( RESET_DAILY_XP_SCRIPT )
    self.db.executeScript( RESET_DAILY_STREAK_SCRIPT )
    self.db.executeScript( RESET_MESSAGED_TODAY_SCRIPT )
    self.logging.send( MODULE, "All daily xp flags reset!" )
    self.db.stop()
    return 

  @resetDailyXPBonus.before_loop
  async def beforeResetDailyXP( self ) -> None:
    """
    Ensures the bot will always reset at 00:00 server time
    Server midnight is 18:00 Mountain or 20:00 EST
    """
    hour, minute = 0, 0
    now = datetime.now()
    future = datetime(now.year, now.month, now.day, hour, minute)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    delta = (future - now).seconds
    hour, minute = delta // 3600, (delta % 3600) // 60

    self.logging.send( MODULE, f"{hour}:{minute} until daily XP reset..." )
    self.logging.printSpacer()

    await asyncio.sleep(delta)

  ##############################################
  # EXP Cog Events
  ##############################################

  @commands.Cog.listener()
  async def on_ready( self ) -> None:
    """
    channel = await self.bot.fetch_channel("881918716454002749")
    message = await channel.fetch_message("882309606611767326")
    CLASS_EMOJI = [
      "🎶", "🛐", "⚔️", "🪄", "🛡️",
      "🏹", "🗡️", "☠️"
    ]
    MEMBER_EMOJI = "✅"
    await message.clear_reactions()
    await message.add_reaction(MEMBER_EMOJI)
    """
    await self.resetDailyXPBonus.start()

  @commands.Cog.listener()
  async def on_message( self, message: Message ) -> None:
    """
    Defines new behavior for the bot on message.
    The EXP Cog listens for each message on the server to award 
    experience to, as long as the user is not a bot. There is a 
    5 second delay between XP awards to discourage spamming.
    """
    await self.bot.wait_until_ready()

    # If the user is a bot
    if message.author == self.bot.user or message.author.bot:
      return

    if message.guild == None:
      return

    guildID = str(message.guild.id)
    userID = str(message.author.id)
    channel = message.channel

    self.guild = message.guild
    self.user = message.author

    currTime = time.time()

    self.connectToDB()
    vals = (userID,)
    self.db.executeScript( CHECK_USER_EXISTS_SCRIPT , vals )
    result = self.db.cursor.fetchone()
    
    # Check if the user is registered on this server yet. 
    if result is None:
      self.logging.send( MODULE, f"{self.user.display_name} not found in database. Creating entry...")
      self.addUser( guildID, userID )

    # Check if the user has sent a message in the last 5 seconds
    userdata = result

    lastTime = userdata[8]
    diff = currTime - float(lastTime)
    if int(diff) < 5:
      # If so, don't award XP
      self.logging.send( MODULE, f"User {self.user.display_name} has messaged too fast! Needs to wait at least 5 seconds for XP gain.")
      self.logging.printSpacer()
      return

    # Set the last message time to our current time
    lastTime = currTime

    # Check if the user is a booster on the server.
    role = discord.utils.find( lambda r: r.name == "Server Booster", message.guild.roles )
    if role in self.user.roles:
      awardedXP = 10
    else:
      awardedXP = 5

    if self.doubleXP:
      awardedXP *= 2

    # Award XP to the user
    self.addExperience( guildID, userID, awardedXP )
    await self.dailyXPBonus( guildID, userID )
    # Check if the user has leveled up.
    await self.levelUp( guildID, userID, channel )

    self.logging.printSpacer()

    self.disconnectFromDB()

    return

  @commands.Cog.listener()
  async def on_raw_reaction_add( self, payload: RawReactionActionEvent ) -> None:

    reaction = payload
    channelID = str(reaction.channel_id)
    channel = await self.bot.fetch_channel(channelID)
    messageID = str(reaction.message_id)
    message = await channel.fetch_message(messageID)
    guildID = str(reaction.guild_id)
    userID = str(reaction.user_id)
    user = await message.guild.fetch_member(userID)
    emoji = str(reaction.emoji)

    if messageID not in REACT_ROLE_MSG_IDS:
      return
    if user == self.bot.user or user.bot:
      return

    # Check which message they reacted to in the list
    if emoji == "🎶":
      classStr = "BARD"
    elif emoji == "🛐":
      classStr = "CLERIC"
    elif emoji == "⚔️":
      classStr = "FIGHTER"
    elif emoji == "🪄":
      classStr = "MAGE"
    elif emoji == "🛡️": 
      classStr = "PALADIN"
    elif emoji == "🏹":
      classStr = "RANGER"
    elif emoji == "🗡️":
      classStr = "ROGUE"
    elif emoji == "☠️":
      classStr = "WARLOCK"

    self.connectToDB()
    vals = (classStr, reaction.user_id)
    self.db.executeScript( UPDATE_USER_CLASS_SCRIPT , vals )

    # Remove reaction from the message
    await message.remove_reaction( emoji, user )

    # Handle output accordingly
    await user.send(f"You've been switched to the '{classStr}' class on `The Backrooms`!")
    self.logging.send( MODULE, f"User '{user.display_name}' has been given '{classStr}' class")
    
    GET_LVL_SCRIPT = """
    SELECT lvl FROM users WHERE user_id = %s;
    """
    vals = (reaction.user_id,)
    self.db.executeScript( GET_LVL_SCRIPT, vals )
    result = self.db.cursor.fetchone()
    lvl = result[0]

    await self.assignXPRole( guildID, userID, lvl, True )

    self.disconnectFromDB()

    return 

  ##############################################
  # EXP Cog Commands
  ##############################################

  @commands.command( name = "adjustlvl" )
  @commands.is_owner()
  async def adjustLevels( self, ctx: Context ) -> None :

    await self.bot.wait_until_ready()

    self.logging.send( MODULE, "Adjusting levels...")
    
    self.connectToDB()
    self.db.executeScript( ADJUST_LVLS_GET_SCRIPT )
    results = self.db.cursor.fetchall()

    for result in results:
      user_id = result[0]
      user = self.bot.fetch_user( user_id )
      xp = result[1]
      lvl = result[2]
      newLvl = int(xp ** (1/5))
      if newLvl > lvl:
        vals = (newLvl, user_id)
        self.db.executeScript( ADJUST_LVLS_SET_SCRIPT, vals)
        self.logging.send( MODULE, f"User '{user}' adjusted from Lvl {lvl} to Lvl {newLvl}")
        await self.assignXPRole( server, user, newLvl, False )

    self.logging.send( MODULE, "All users on server adjusted!")

    return 

  @commands.command( name = "givexp" , aliases = ["gxp"] )
  @commands.is_owner()
  async def giveXP( self, ctx: Context, *args ):
    try:
      self.connectToDB()
      user_id = str(args[0])
      vals = (user_id,)
      self.db.executeScript( CHECK_USER_EXISTS_SCRIPT, vals )
      result = self.db.cursor.fetchone() 
      if result is None:
        await ctx.send( f"{user_id} not found in database. Creating entry..." )
        await self.addUser( guild_id, user_id )

      xp = int(args[1])
      guild_id = str(ctx.guild.id)
      channel = ctx.channel
      self.addExperience( guild_id , user_id, xp )
      await self.levelUp( guild_id, user_id, channel )
      userdata = db[guild_id][user_id]
      xp_total = userdata["experience"]
      self.logging.send( MODULE, f"Manually adjusted {user_id} XP by {xp}. New total: {xp_total} XP." )
    except:
      await ctx.send( "ERROR: There was something wrong with adjusting that users XP. Try again with a valid user ID and amount. ")
    self.disconnectFromDB()
    return

  @commands.command( name = "leaderboard" , aliases = ["lb"])
  async def checkLeaderboard( self, ctx: Context ) -> None:
    """
    Allows users to check who has the most experience on the server.
    Uses a 'asciidoc' code block to display info neatly.
    """
    message = ctx.message 
    guildID = str(message.guild.id)

    # Sort the users by experience
    self.connectToDB()
    self.db.executeScript( LEADERBOARD_SCRIPT )
    results = self.db.cursor.fetchall()
    
    # Check if we have 10 users to make a leaderboard with
    if len(results) >= 10:
      lbLength = 10
    # Otherwise, only grab the length of the list
    else:
      lbLength = len(results)

    guildName = message.guild.name
    leaderboardStr = f"```asciidoc\nLeaderboard - {guildName}\n==============================\n"
    # For each user, Format data and add to leaderboard string to send
    lvlStrLen = len(str(results[0][2]))
    xpStrLen = len(str(results[0][1]))
    i = 0
    for result in results:
      user = await message.guild.fetch_member(int(result[0]))
      userNickname = user.display_name
      leaderboardStr += f"{i+1}. {userNickname:<25} | Level {result[2]:>{lvlStrLen}} | {result[1]:>{xpStrLen}} Total XP\n".format()
      i += 1
    leaderboardStr += "```"
        
    # Send leaderboard string out
    await ctx.send(leaderboardStr)
    return
  
  @commands.command( name = "progression" , aliases = ["prog"])
  async def checkProgression( self, ctx: None , *args ) -> None :
    
    await self.bot.wait_until_ready()

    message = ctx.message
    guildID = str(message.guild.id)
    userID = str(message.author.id)
    
    self.connectToDB()
    vals = (userID,)
    self.db.executeScript( CHECK_PROG_SCRIPT , vals )
    result = self.db.cursor.fetchone()

    # Get Rank List for user's class
    exp = result[1]
    lvl = result[2]
    userClass = result[0]

    if userClass is None:
      userClass = "NONE"
      rankList = BASIC_XP_ROLES
    elif userClass == "BARD":
      rankList = BARD_XP_ROLES
    elif userClass == "CLERIC":
      rankList = CLERIC_XP_ROLES
    elif userClass == "FIGHTER":
      rankList = FIGHTER_XP_ROLES
    elif userClass == "MAGE":
      rankList = MAGE_XP_ROLES
    elif userClass == "PALADIN":
      rankList = PALADIN_XP_ROLES
    elif userClass == "RANGER":
      rankList = RANGER_XP_ROLES
    elif userClass == "ROGUE":
      rankList = ROGUE_XP_ROLES
    elif userClass == "WARLOCK":
      rankList = WARLOCK_XP_ROLES

    progList = rankList.copy()
    progList.reverse()

    progressStr = f"```asciidoc\nClass Progression - {userClass} - {message.author}\n==============================\n"
    i = 10
    for rank in progList:
      rankStr = re.sub(r"\([^()]*\)", "", rank).strip()
      if i < 10:
        space = "  "
      else:
        space = " "
      progressStr += f"{i}.{space} {rankStr:<30}"
      xpLimit = i ** 5
      progressStr += f" | {xpLimit:>6} XP"
      if i == lvl:
        progressStr += " :: [X]\n"
      else:
        progressStr += "\n"
      i -= 1
    progressStr += "\n"
    if lvl < 10:
      xpLimit = (lvl + 1) ** 5
      percent = (exp / xpLimit) * 100
      progressStr += f"[PROGRESS TO NEXT RANK: {exp:>6} / {xpLimit:>6} ({percent:.2f}%)]\n"
    else:
      progressStr += f"[MAX RANK ACHIEVED: {exp:>6} TOTAL XP]\n"
    progressStr += "```"

    await ctx.send(progressStr)
    return

  @commands.command( name = "rank" )
  async def checkRank( self, ctx: Context ) -> None:
    """
    Allows a user to see their own rank on the server. 
    Rank includes:
    - Experience Total
    - Level
    - Server Booster Status
    """
    await self.bot.wait_until_ready()

    message = ctx.message
    guildID = str(message.guild.id)
    userID = str(message.author.id)

    self.connectToDB()
    vals = (userID, )
    self.db.executeScript( CHECK_RANK_SCRIPT , vals )
    result = self.db.cursor.fetchone()

    experience = result[1]
    lvl = result[2]
    classStr = result[3]
    rankStr = result[4]

    userNickname = message.author.display_name
    userPicURL = str(message.author.avatar_url)

    # if the users name ends with s or x, change the possesive string
    if userNickname.endswith("s") or userNickname.endswith("x"):
      possesive = "'"
    else:
      possesive = "'s"

    # Check if the user is a server booster or not
    role = discord.utils.find( lambda r: r.name == "Server Booster", message.guild.roles )

    if role in message.author.roles:
      boosterStr = "YES (x2 XP)"
    else:
      boosterStr = "NO"

    # Create the embed for rank 
    embed = discord.Embed(
      title = f"{userNickname}{possesive} Stats",
      color = discord.Colour.random()
    )
    embed.set_footer( text = f"UID: {message.author.id}" )
    embed.set_thumbnail( url = userPicURL )
    embed.add_field(
      name = "Class:",
      inline = True,
      value = classStr
    )
    embed.add_field(
      name = "Level:",
      inline = True,
      value = lvl
    )
    embed.add_field(
      name = "Rank:",
      inline = True, 
      value = rankStr
    )
    embed.add_field(
      name = "Total XP:",
      inline = True,
      value = experience
    )
    embed.add_field(
      name = "Server Booster?",
      inline = True,
      value = boosterStr
    )

    # Send the embed to the chat
    await ctx.send(embed = embed)
    return 

  @commands.command( name = "doublexp", aliases = ["dxp"] )
  @commands.is_owner()
  async def toggleDoubleXP( self, ctx: Context ) -> None:
    """
    Allows the owner(s) of the server to toggle Double XP for the server.
    """
    if self.doubleXP:
      self.doubleXP = False 
      await ctx.send("Double XP has been disabled!")
      return 
    self.doubleXP = True 
    await ctx.send("Double XP has been activated!")
    return


  ##############################################
  # Support Functions 
  ############################################## 

  # Async Support Functions

  async def assignXPRole( self, guild_id: str, user_id: str , lvl : int, notify_user: bool ) -> None:
    """
    Assigns the XP role to user based on given user_id, guild_id, level. Depending on input, will / will not notify
    the user that their XP has been adjusted or changed.
    """
    guild = await self.bot.fetch_guild( guild_id )
    user = await guild.fetch_member( user_id )
    
    await self.removeOldRoles( guild, user )

    # Assign Basic Role
    basicRoleStr = BASIC_XP_ROLES[lvl-1]
    role = discord.utils.get( guild.roles , name = basicRoleStr )
    await user.add_roles( role )
    
    self.connectToDB()

    vals = (user_id,)
    self.db.executeScript( ASSIGN_XP_GET_SCRIPT , vals )
    result = self.db.cursor.fetchone()

    userClass = result[0]

    # Get the role category 
    if userClass is None:
      roleList = BASIC_XP_ROLES
    if userClass == "BASIC":
      roleList = BASIC_XP_ROLES
    elif userClass == "BARD":
      roleList = BARD_XP_ROLES
    elif userClass == "CLERIC":
      roleList = CLERIC_XP_ROLES
    elif userClass == "FIGHTER":
      roleList = FIGHTER_XP_ROLES
    elif userClass == "MAGE":
      roleList = MAGE_XP_ROLES
    elif userClass == "PALADIN":
      roleList = PALADIN_XP_ROLES
    elif userClass == "RANGER":
      roleList = RANGER_XP_ROLES
    elif userClass == "ROGUE":
      roleList = ROGUE_XP_ROLES
    elif userClass == "WARLOCK":
      roleList = WARLOCK_XP_ROLES

    # Get the role in discord
    roleStr = roleList[lvl-1]
    role = discord.utils.get( guild.roles, name = roleStr )

    # Assign the role to the user
    await user.add_roles( role )
    roleStr = re.sub(r"\([^()]*\)", "", roleStr).strip()
    
    vals = ( roleStr , user_id )
    self.db.executeScript( ASSIGN_XP_SET_SCRIPT , vals )

    # Let the user know they earned a new role through DM.
    if notify_user:
      await user.send(f"Congrats! You've been assigned the '{roleStr}' role on `The Backrooms`!!")

    return

  async def dailyXPBonus( self, guild_id: str, user_id: str ) -> None:
    """
    Determines whether or not the user has earned their daily xp. Calculates daily xp if so and awards it to the user.
    """
    self.connectToDB()
    DAILY_XP_GET_SCRIPT = """
    SELECT daily_xp_earned , daily_xp_streak FROM users WHERE user_id = %s;
    """
    DAILY_XP_SET_SCRIPT = """
    UPDATE users SET daily_xp_earned = %s, daily_xp_streak = %s, messaged_today = %s WHERE user_id = %s;
    """
    
    vals = (user_id,)
    self.db.executeScript( DAILY_XP_GET_SCRIPT , vals )
    result = self.db.cursor.fetchone()
    dailyXPEarned = result[0]
    dailyXPStreak = result[1]

    # If the user has already gotten their daily xp bonus
    if dailyXPEarned:
      return 

    # If the users daily xp bonus is less than 7
    if dailyXPStreak < 14:
      dailyXPStreak += 1

    # Award XP and update db
    awardedXP = dailyXPStreak * 5
    self.addExperience( guild_id , user_id, awardedXP )

    vals = ( True, dailyXPStreak, True , user_id )
    self.db.executeScript( DAILY_XP_SET_SCRIPT , vals )

    # Notify user and console
    await self.user.send(f"You've earned your daily XP bonus ({awardedXP}) for messaging on `The Backrooms`! You now have a {dailyXPStreak}-day streak. Keep it up!")
    self.logging.send( MODULE, f"User {self.user.display_name} has earned their daily XP bonus. {dailyXPStreak} day streak = {awardedXP} bonus XP")

    return

  async def levelUp( self, guild_id: str, user_id: str, channel: discord.TextChannel ) -> None:
    """
    Support function for 'on_message' event.
    Determines whether or not the given user has leveled up. If so,
    displays that in chat for the user and updates their db. 
    """
    CHECK_LVL_SCRIPT = """
    SELECT xp, lvl FROM users WHERE user_id = %s;
    """
    SET_LVL_SCRIPT = """
    UPDATE users SET lvl = %s WHERE user_id = %s;
    """
    self.connectToDB()
    vals = (user_id,)
    self.db.executeScript( CHECK_LVL_SCRIPT, vals )
    result = self.db.cursor.fetchone()

    experience = result[0]
    lvlStart = result[1]

    # This will round down to the nearest whole number
    lvlEnd = int(experience ** (1/5))

    # if our level is already at the cap
    if lvlEnd > 10:
      return 

    # EX: If our curr lvl is 4 and our calc level is 5
    if lvlStart < lvlEnd:
      vals = (lvlEnd, user_id)
      self.db.executeScript( SET_LVL_SCRIPT , vals )
      await channel.send( f"{self.user.mention} has leveled up to Level {lvlEnd}!")
      self.logging.send( MODULE, f"{self.user.display_name} has leveled up to Level {lvlEnd}!")
      await self.assignXPRole( guild_id, user_id, lvlEnd, True )
    
    return

  async def removeOldRoles( self, guild: Guild, member: Member ) -> None:
    for roleList in ROLE_LISTS:
      for roleStr in roleList:
        role = discord.utils.get( guild.roles, name = roleStr )
        if role in member.roles:
          await member.remove_roles( role )
          self.logging.send( MODULE, f"Removed Role {role.name} from User {member.display_name}" )
    return 

  # Synchronous Support Functions

  def addExperience( self, guild_id : str, user_id : str, exp : int ) -> None:
    """
    Support function for 'on_message' event.
    Increments experience for the given user on the given server.
    """
    ADD_XP_SCRIPT = """
    UPDATE users SET xp = %s WHERE user_id = %s;
    """
    GET_XP_SCRIPT = """
    SELECT xp FROM users WHERE user_id = %s;
    """
    self.connectToDB()
    vals = (user_id,)
    self.db.executeScript( GET_XP_SCRIPT, vals)
    result = self.db.cursor.fetchone()
    totalXP = result[0] + exp
    vals = (totalXP, user_id )
    self.db.executeScript( ADD_XP_SCRIPT , vals )
    vals = (user_id,)
    totalXP = result[0]
    self.logging.send( MODULE, f"{self.user.display_name} has earned {exp} XP. Current total: {totalXP} XP." )
    return

  def addUser( self, guild_id: str, user_id: str ) -> None:
    """
    Support function for 'on_message' event. 
    Adds a user on a given server to the replit database.
    """
    currTime = time.time()
    # Adds the user's data dictionary to the Replit DB
    ADD_USER_SCRIPT = """
    INSERT INTO users
      (user_id, xp, lvl, class_name, rank_name, daily_xp_earned, daily_xp_streak, last_message, messaged_today )
    VALUES
      (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    self.connectToDB( self )
    vals = ( user_id, 5, 1, "NONE", "NONE", False, 0, currTime, False )
    self.db.executeScript( ADD_USER_SCRIPT, vals )
    self.logging.send( MODULE, f"Added user '{self.user.display_name}' to database.")
    return
    
  def connectToDB( self ) -> None:
    if not self.db.openDB:
      self.db.start()
    return 
    
  def disconnectFromDB( self ) -> None:
    if self.db.openDB:
      self.db.stop()
    return

  # End of Exp Cog

##############################################
# Setup Command for Bot
##############################################
def setup( bot: Bot ) -> None:
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( Exp( bot ) )
