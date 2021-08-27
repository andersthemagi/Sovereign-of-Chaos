
import database
import discord 
import time

from discord.ext import commands
from replit import db

USE_REPL = True

ADD_USER_SCRIPT = """
INSERT INTO server_list
(server_id, user_id, experience, lvl , last_message )
VALUES (%s, %s, %s, %s, %s);
"""
ADD_XP_SCRIPT = """
UPDATE server_list SET experience = experience + %s WHERE server_id = %s AND user_id = %s;
"""
CHECK_USER_LAST_MSG_EXISTS_SCRIPT = """
SELECT last_message FROM server_list WHERE server_id = %s AND user_id = %s;
"""
CHECK_USER_EXISTS_SCRIPT = """
SELECT * FROM server_list WHERE server_id = %s AND user_id = %s;
"""
GET_USER_STATS_SCRIPT = """
SELECT experience, lvl FROM server_list WHERE server_id = %s AND
user_id = %s
"""
GET_XP_SCRIPT = """
SELECT experience FROM server_list WHERE server_id = %s AND user_id = %s;
"""
UPDATE_LAST_MSG_SCRIPT = """
UPDATE server_list SET last_message = %s WHERE server_id = %s AND user_id = %s;
"""
UPDATE_LVL_SCRIPT = """
UPDATE server_list SET lvl = %s WHERE server_id = %s AND user_id = %s
"""

class Exp( commands.Cog, name = "Exp" ):

  def __init__( self, bot ):
    self.bot = bot 
    self.db = database.DB()

  @commands.Cog.listener()
  async def on_message( self, message ):
    """
    Defines new behavior for the bot on message
    """
    await self.bot.wait_until_ready()

    if message.author == self.bot.user or message.author.bot:
      return

    guildID = str(message.guild.id)
    userID = str(message.author.id)
    channel = message.channel

    self.guild = message.guild
    self.user = message.author

    if USE_REPL:

      server = db[guildID]
      
      if userID not in server.keys():
        print(f"{self.user.display_name} not found in database. Creating entry...")
        self.addUser( guildID, userID )

      role = discord.utils.find( lambda r: r.name == "Server Booster", message.guild.roles )

      if role in self.user.roles:
        awardedXP = 10
      else:
        awardedXP = 5

      self.addExperience( guildID, userID, awardedXP )
      await self.levelUp( guildID, userID, channel )

      self.db.stop()

      print( '------' )

      return

    self.db.start()

    vals = (guildID, userID)
    self.db.executeScript(CHECK_USER_EXISTS_SCRIPT, vals)
    result = self.db.cursor.fetchone()

    if result is None:
      print(f"{self.user.display_name} not found in database. Creating entry...")
      self.addUser( guildID, userID )

    currTime = time.time()

    self.db.executeScript(CHECK_USER_LAST_MSG_EXISTS_SCRIPT, vals)
    result = self.db.cursor.fetchone()

    if result[0] is None:
      lastTime = time.time()
      vals = (lastTime, guildID, userID)
      self.db.executeScript(UPDATE_LAST_MSG_SCRIPT, vals )
    else:
      lastTime = result[0]
      diff = currTime - float(lastTime)
      print(diff)
      if int(diff) < 5:
        print("User has messaged too fast! Needs to wait at least 5 seconds for XP gain.")
        self.db.stop()
        print( '------' )
        return
      vals = (currTime, guildID, userID)
      self.db.executeScript(UPDATE_LAST_MSG_SCRIPT, vals )

    role = discord.utils.find( lambda r: r.name == "Server Booster", message.guild.roles )

    if role in self.user.roles:
      awardedXP = 10
    else:
      awardedXP = 5

    self.addExperience( guildID, userID, awardedXP )
    await self.levelUp( guildID, userID, channel )

    self.db.stop()

    print( '------' )

    return

  @commands.command( name = "rank" )
  async def checkRank( self, ctx ):
    message = ctx.message
    guildID = str(message.guild.id)
    userID = str(message.author.id)

    if USE_REPL:
      userdata = db[guildID][userID]
      experience = userdata["experience"]
      lvl = userdata["lvl"]
    else:
      vals = (guildID, userID)

      self.db.start()
      self.db.executeScript(GET_USER_STATS_SCRIPT, vals)
      result = self.db.cursor.fetchone()
      experience = result[0]
      lvl = result[1]

    userNickname = message.author.display_name
    userPicURL = str(message.author.avatar_url)

    if userNickname.endswith("s") or userNickname.endswith("x"):
      possesive = "'"
    else:
      possesive = "'s"

    role = discord.utils.find( lambda r: r.name == "Server Booster", message.guild.roles )

    if role in message.author.roles:
      boosterStr = "YES (x2 XP)"
    else:
      boosterStr = "NO"

    embed = discord.Embed(
      title = f"{userNickname}{possesive} Stats",
      color = discord.Colour.random()
    )
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

    await ctx.send(embed = embed)

    if not USE_REPL:
      self.db.stop()

    return 

  @commands.command( name = "leaderboard" , aliases = ["lb"])
  async def checkLeaderboard( self, ctx ):
    
    message = ctx.message 
    guildID = str(message.guild.id)

    if USE_REPL:
      serverdata = db[guildID]
      serverdata = list(serverdata.items())

      users = []
      for item in serverdata:
        foundID = item[0]
        experience = int(item[1]["experience"])
        lvl = int(item[1]["lvl"])
        users.append( (foundID, experience, lvl) )

      length = len(users)
      for i in range( 0, length ):
        for j in range( 0, length - i - 1 ):
          if (users[j][1] < users[j + 1][1]):
            temp = users[j]
            users[j] = users[j + 1] 
            users[j + 1] = temp

      if len(users) >= 10:
        lbLength = 10
      else:
        lbLength = len(users)

      guildName = message.guild.name
      leaderboardStr = f"```md\nLeaderboard - {guildName}\n==============================\n"
      for i in range( 0, lbLength ):
        userdata = users[i]
        user = await message.guild.fetch_member(int(userdata[0]))
        leaderboardStr += f"{i+1}. {user.display_name:<20} | Level {userdata[2] } | {userdata[1]} Total XP\n"
      leaderboardStr += "```"
        
      
    else:
      GET_LEADERBOARD_SCRIPT = f"""
      SELECT user_id, experience, lvl FROM server_list WHERE server_id = {guildID} ORDER BY experience DESC, lvl DESC LIMIT 10;
      """

      self.db.start()
      self.db.executeScript(GET_LEADERBOARD_SCRIPT)
      result = self.db.cursor.fetchall()

      guildName = message.guild.name
      leaderboardStr = f"```md\nLeaderboard - {guildName}\n==============================\n"
      place = 1
      for row in result:
        userID = row[0]
        experience = row[1]
        lvl = row[2]
        user = await message.guild.fetch_member(int(userID))
        leaderboardStr += f"{place}. {user.display_name : <20} | Level {lvl} | {experience} Total XP\n"
        place += 1
      leaderboardStr += "```"
    await ctx.send(leaderboardStr)
    self.db.stop()
    return 

  def addUser( self, guild_id: str, user_id: str ):
    if USE_REPL:
      currTime = time.time()
      db[guild_id][user_id] = {
        "experience" : 0,
        "lvl" : 1,
        "last_message" : currTime,
      }
      print(f"Added user '{self.user.display_name}' to database.")
      return 
    currTime = time.time()
    vals = (guild_id, user_id, 0, 1, currTime)
    self.db.executeScript(ADD_USER_SCRIPT, vals )
    print(f"Added user '{self.user.display_name}' to database.")
    return 

  def addExperience( self, guild_id : str, user_id : str, exp : int ):

    if USE_REPL:
      db[guild_id][user_id]["experience"] += exp
      totalXP = db[guild_id][user_id]["experience"]
      print(f"{self.user.display_name} has earned {exp} XP. Current total: {totalXP} XP." )
      return

    vals = (exp, guild_id, user_id)
    self.db.executeScript( ADD_XP_SCRIPT , vals )
    vals = (guild_id, user_id)
    self.db.executeScript( GET_XP_SCRIPT , vals )
    result = self.db.cursor.fetchone()
    totalXP = int(result[0])

    print(f"{self.user.display_name} has earned {exp} XP. Current total: {totalXP} XP." )
    return

  async def levelUp( self, guild_id: str, user_id: str, channel: discord.TextChannel ):

    if USE_REPL:
      userdata = db[guild_id][user_id]
      experience = userdata["experience"]
      lvlStart = userdata["lvl"]
      lvlEnd = int(experience ** (1/4))

      if lvlStart < lvlEnd:
        userdata["lvl"] = lvlEnd
        await channel.send( f"{self.user.mention} has leveled up to Level {lvlEnd}!")
        print( f"{self.user.display_name} has leveled up to Level {lvlEnd}!")
      
      return

    vals = (guild_id, user_id)
    self.db.executeScript(GET_USER_STATS_SCRIPT, vals)
    result = self.db.cursor.fetchone()

    experience = int(result[0])
    lvlStart = int(result[1])
    lvlEnd = int(experience ** (1/4))

    if lvlStart < lvlEnd:
      vals = (lvlEnd, guild_id, user_id)
      self.db.executeScript(UPDATE_LVL_SCRIPT, vals)
      await channel.send( f"{self.user.mention} has leveled up to Level {lvlEnd}!")
      print( f"{self.user.display_name} has leveled up to Level {lvlEnd}!")

    return

  # End of Exp Cog

def setup(bot):
  print("Attempting load of 'Exp' extension...")
  bot.add_cog( Exp( bot ) )