##############################################
# Package Imports
##############################################
import discord 
import time

from discord.ext import commands
from replit import db

##############################################
# EXP Cog
##############################################

class Exp( commands.Cog, name = "Exp" ):

  def __init__( self, bot ):
    self.bot = bot 

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

    # Award XP to the user
    self.addExperience( guildID, userID, awardedXP )
    # Check if the user has leveled up.
    await self.levelUp( guildID, userID, channel )

    print( '------' )

    return

  ##############################################
  # EXP Cog Commands
  ##############################################

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
    for i in range( 0, lbLength ):
      userdata = users[i]
      user = await message.guild.fetch_member(int(userdata[0]))
      userNickname = user.display_name
      leaderboardStr += f"{i+1}. {userNickname:<25} | Level {userdata[2] } | {userdata[1]} Total XP\n"
    leaderboardStr += "```"
        
    # Send leaderboard string out
    await ctx.send(leaderboardStr)
    return

  ##############################################
  # Support Functions 
  ############################################## 

  # Async Support Functions

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
    lvlEnd = int(experience ** (1/4))

    # EX: If our curr lvl is 4 and our calc level is 5
    if lvlStart < lvlEnd:
      userdata["lvl"] = lvlEnd
      await channel.send( f"{self.user.mention} has leveled up to Level {lvlEnd}!")
      print( f"{self.user.display_name} has leveled up to Level {lvlEnd}!")
    
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
      "last_message" : currTime,
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