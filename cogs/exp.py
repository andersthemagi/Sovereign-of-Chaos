##############################################
# Package Imports
##############################################
import asyncio
import discord 
import time

from datetime import datetime
from discord.ext import commands, tasks
from replit import db

##############################################
# Constants
##############################################

REACT_ROLE_MSG_IDS = [
  "882013329411948606"
]

BASIC_XP_ROLES = [
  "Level 1", "Level 2", "Level 3", "Level 4", "Level 5", 
  "Level 6", "Level 7", "Level 8", "Level 9", "Level 10"
]

BARD_XP_ROLES = [
  "Lyrist (LVL 1)", "Ryymer (LVL 2)", "Sonateer (LVL 3)",
  "Skald (LVL 4)", "Racaraide (LVL 5)", "Joungleur (LVL 6)",
  "Troubadour (LVL 7)", "Minstrel (LVL 8)", "Lorist (LVL 9)",
  "Master Lorist (LVL 10)"
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
  BASIC_XP_ROLES, BARD_XP_ROLES, FIGHTER_XP_ROLES, MAGE_XP_ROLES,
  PALADIN_XP_ROLES, RANGER_XP_ROLES, ROGUE_XP_ROLES, WARLOCK_XP_ROLES
]


##############################################
# EXP Cog
##############################################

class Exp( commands.Cog, name = "Exp" ):

  def __init__( self, bot ):
    self.bot = bot 
    self.doubleXP = False

  ##############################################
  # EXP Cog Async Tasks
  ##############################################

  @tasks.loop(hours = 24)
  async def resetDailyXPBonus( self ):
    """
    Resets the daily xp bonus flags to allow players to earn bonus xp again.
    """
    print(f"{self.getTimeStr()} Resetting daily xp flags.")
    servers = db.keys()
    # For each server listed
    for server in servers:
      users = db[server].keys()
      # For each user in the server
      for user in users:
        userdata = db[server][user]
        # Reset the daily_xp_earned flag
        userdata["daily_xp_earned"] = False 
        # If they haven't messaged today
        if userdata["messaged_today"] == False:
          # Reset their streak
          userdata["daily_xp_streak"] = 0
        userdata["messaged_today"] = False 
    print(f"{self.getTimeStr()}All daily xp flags reset!")
    return 

  @resetDailyXPBonus.before_loop
  async def beforeResetDailyXP():
    """
    Ensures the bot will always reset at 00:00 server time
    """
    hour, minute = 0, 0
    now = datetime.now()
    future = datetime(now.year, now.month, now.day + 1, hour, minute)
    delta = (future - now).seconds
    await asyncio.sleep(delta)

  ##############################################
  # EXP Cog Events
  ##############################################

  @commands.Cog.listener()
  async def on_message( self, message ):
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

    server = db[guildID]
    
    # Check if the user is registered on this server yet. 
    if userID not in server.keys():
      print(f"{self.getTimeStr()}{self.user.display_name} not found in database. Creating entry...")
      self.addUser( guildID, userID )

    # Check if the user has sent a message in the last 5 seconds
    userdata = server[userID]
    lastTime = userdata["last_message"]
    diff = currTime - float(lastTime)
    if int(diff) < 5:
      # If so, don't award XP
      print(f"{self.getTimeStr()}User {self.user.display_name} has messaged too fast! Needs to wait at least 5 seconds for XP gain.")
      print( '------' )
      return

    # Set the last message time to our current time
    userdata["last_message"] = currTime

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
    print( '------' )

    return

  @commands.Cog.listener()
  async def on_raw_reaction_add( self, RawReactionActionEvent ):

    reaction = RawReactionActionEvent
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

    db[guildID][userID]["class"] = classStr

    # Remove reaction from the message
    await message.remove_reaction( emoji, user )

    # Handle output accordingly
    await user.send(f"You've been switched to the '{classStr}' class on `The Backrooms`!")
    print(f"{self.getTimeStr()} User '{user.display_name}' has been given '{classStr}' class")

    await self.assignXPRole( guildID, userID, db[guildID][userID]["lvl"], True )

    return 

  ##############################################
  # EXP Cog Commands
  ##############################################

  @commands.command( name = "assign" )
  @commands.is_owner()
  async def assignRolesCommand( self, ctx ):
    print(f"{self.getTimeStr()} Assigning xp roles...")
    servers = db.keys()

    # For each server listed
    for server in servers:
      users = db[server].keys()
      # For each user in the server
      for user in users:
        userdata = db[server][user]
        await self.assignXPRole( server, user , userdata["lvl"] , False )
        
    print(f"{self.getTimeStr()} All users assigned xp roles!")
    return

  @commands.command( name = "adjustlvl" )
  @commands.is_owner()
  async def adjustLevels( self, ctx ):
    print(f"{self.getTimeStr()} Adjusting levels...")
    servers = db.keys()
    for server in servers:
      users = db[server].keys()
      for user in users:
        userdata = db[server][user]
        experience = userdata["experience"]
        lvl = userdata["lvl"]
        newLvl = int(experience ** (1/5))
        userdata["lvl"] = newLvl
        print(f"{self.getTimeStr()} User '{user}' adjusted from Lvl {lvl} to Lvl {newLvl}")
        await self.assignXPRole( server, user, newLvl, False )
    print(f"{self.getTimeStr()} All users on server adjusted!")

  @commands.command( name = "leaderboard" , aliases = ["lb"])
  async def checkLeaderboard( self, ctx ):
    """
    Allows users to check who has the most experience on the server.
    Uses a 'asciidoc' code block to display info neatly.
    """
    message = ctx.message 
    guildID = str(message.guild.id)

    serverdata = db[guildID]
    serverdata = list(serverdata.items())

    users = []
    # Get all the users in the server
    for item in serverdata:
      foundID = item[0]
      experience = int(item[1]["experience"])
      lvl = int(item[1]["lvl"])
      users.append( (foundID, experience, lvl) )

    # Sort the users by experience
    users.sort( key= lambda x: x[1] , reverse = True )

    # Check if we have 10 users to make a leaderboard with
    if len(users) >= 10:
      lbLength = 10
    # Otherwise, only grab the length of the list
    else:
      lbLength = len(users)

    guildName = message.guild.name
    leaderboardStr = f"```asciidoc\nLeaderboard - {guildName}\n==============================\n"
    # For each user, Format data and add to leaderboard string to send
    lvlStrLen = len(str(users[0][2]))
    xpStrLen = len(str(users[0][1]))
    for i in range( 0, lbLength ):
      userdata = users[i]
      user = await message.guild.fetch_member(int(userdata[0]))
      userNickname = user.display_name
      leaderboardStr += f"{i+1}. {userNickname:<25} | Level {userdata[2]:>{lvlStrLen}} | {userdata[1]:>{xpStrLen}} Total XP\n".format()
    leaderboardStr += "```"
        
    # Send leaderboard string out
    await ctx.send(leaderboardStr)
    return

  @commands.command( name = "rank" )
  async def checkRank( self, ctx ):
    """
    Allows a user to see their own rank on the server. 
    Rank includes:
    - Experience Total
    - Level
    - Server Booster Status
    """
    message = ctx.message
    guildID = str(message.guild.id)
    userID = str(message.author.id)

    userdata = db[guildID][userID]
    experience = userdata["experience"]
    lvl = userdata["lvl"]

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
      description = f"Server: {message.guild.name}",
      color = discord.Colour.random()
    )
    embed.set_footer( text = f"UID: {message.author.id}" )
    embed.set_thumbnail( url = userPicURL )
    embed.add_field(
      name = "Level:",
      inline = True,
      value = lvl
    )
    embed.add_field(
      name = "Total XP:",
      inline = True,
      value = experience
    )
    embed.add_field(
      name = "Server Booster?",
      inline = False,
      value = boosterStr
    )

    # Send the embed to the chat
    await ctx.send(embed = embed)
    return 

  @commands.command( name = "doublexp", aliases = ["dxp"] )
  @commands.is_owner()
  async def toggleDoubleXP( self, ctx ):
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

  async def assignXPRole( self, guild_id: str, user_id: str , lvl : int, notify_user: bool ):

    userdata = db[guild_id][user_id]
    guild = await self.bot.fetch_guild( guild_id )
    user = await guild.fetch_member( user_id )
    
    keys = userdata.keys()
    # Check if the user has a category
    # ERROR CASE: If the user is pre-XP roles implementation
    if "class" not in keys:
      print(f"{self.getTimeStr} User {user.display_name} has no class variable. Creating one for them.")
      userdata["class"] = None
    
    await self.removeOldRoles( guild, user )

    # Assign Basic Role
    basicRoleStr = BASIC_XP_ROLES[lvl-1]
    role = discord.utils.get( guild.roles , name = basicRoleStr )
    await user.add_roles( role )


    userClass = userdata["class"]

    # Get the role category 
    if userClass is None:
      roleList = BASIC_XP_ROLES
    elif userClass == "BARD":
      roleList = BARD_XP_ROLES
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

    # Let the user know they earned a new role through DM.
    if notify_user:
      await user.send(f"Congrats! You've been assigned the '{roleStr}' role on `The Backrooms`!!")

    return

  async def dailyXPBonus( self, guild_id: str, user_id: str ):
    try:
      userdata = db[guild_id][user_id]
      dailyXPEarned = userdata["daily_xp_earned"]
      dailyXPStreak = userdata["daily_xp_streak"]
    except:
      print(f"{self.getTimeStr()}ERROR: User needs to be given daily XP stats. ")
      userdata["daily_xp_earned"] = False 
      userdata["daily_xp_streak"] = 0
      userdata["messaged_today"] = False 
      dailyXPEarned = userdata["daily_xp_earned"]
      dailyXPStreak = userdata["daily_xp_streak"]

    if dailyXPEarned:
      return 

    if dailyXPStreak < 7:
      dailyXPStreak += 1

    awardedXP = dailyXPStreak * 5

    print(f"{self.getTimeStr()}User {self.user.display_name} has earned their daily XP bonus. {dailyXPStreak} day streak = {awardedXP} bonus XP")
    self.addExperience( guild_id , user_id, awardedXP )

    userdata["daily_xp_earned"] = True
    userdata["daily_xp_streak"] = dailyXPStreak
    userdata["messaged_today"] = True

    await self.user.send(f"You've earned your daily XP bonus ({awardedXP}) for messaging on `The Backrooms`! You now have a {dailyXPStreak}-day streak. Keep it up!")

    return

  async def levelUp( self, guild_id: str, user_id: str, channel: discord.TextChannel ):
    """
    Support function for 'on_message' event.
    Determines whether or not the given user has leveled up. If so,
    displays that in chat for the user and updates their db. 
    """

    userdata = db[guild_id][user_id]
    experience = userdata["experience"]
    lvlStart = userdata["lvl"]

    # This will round down to the nearest whole number
    lvlEnd = int(experience ** (1/5))

    # EX: If our curr lvl is 4 and our calc level is 5
    if lvlStart < lvlEnd:
      userdata["lvl"] = lvlEnd
      await channel.send( f"{self.user.mention} has leveled up to Level {lvlEnd}!")
      print( f"{self.user.display_name} has leveled up to Level {lvlEnd}!")
      await self.assignXPRole( guild_id, user_id, lvlEnd )
    
    return

  async def removeOldRoles( self, guild, user ):
    for roleList in ROLE_LISTS:
      for roleStr in roleList:
        role = discord.utils.get( guild.roles, name = roleStr )
        if role in user.roles:
          await user.remove_roles( role )
          print(f"Removed Role {role.name} from User {user.display_name}")
    return 

  # Synchronous Support Functions

  def addExperience( self, guild_id : str, user_id : str, exp : int ):
    """
    Support function for 'on_message' event.
    Increments experience for the given user on the given server.
    """
    db[guild_id][user_id]["experience"] += exp
    totalXP = db[guild_id][user_id]["experience"]
    print(f"{self.getTimeStr()}{self.user.display_name} has earned {exp} XP. Current total: {totalXP} XP." )
    return

  def addUser( self, guild_id: str, user_id: str ):
    """
    Support function for 'on_message' event. 
    Adds a user on a given server to the replit database.
    """
    currTime = time.time()
    # Adds the user's data dictionary to the Replit DB
    db[guild_id][user_id] = {
      "experience" : 5,
      "lvl" : 1,
      "class": None,
      "daily_xp_earned" : False,
      "daily_xp_streak" : 0,
      "last_message" : currTime,
      "messaged_today"  : False,
    }
    print(f"{self.getTimeStr()}Added user '{self.user.display_name}' to database.")
    return 

  def getTimeStr( self ):
    """
    Returns a formatted string with the current time for logging events.
    """
    return time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime())

  # End of Exp Cog

def setup(bot):
  print("Attempting load of 'Exp' extension...")
  bot.add_cog( Exp( bot ) )