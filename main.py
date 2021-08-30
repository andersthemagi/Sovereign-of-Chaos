##############################################
# Package Imports
##############################################

import discord
import discord.ext
import os
import sys
sys.path.insert(1, './cogs/support')

from timer import Timer

from discord.ext import commands
from flask import Flask
from replit import db
from threading import Thread

##############################################
# Constants and Setup
##############################################

app = Flask( 'discord bot' )

OWNER_ID = os.getenv( "OWNER_ID" )

# Initialize Bot with cmd prefix
bot = commands.Bot( 
  command_prefix = '!',
  owner = OWNER_ID )
bot.remove_command( 'help' )

DB_SETUP_PATH = "scripts/travelerdb-setup.sql"

loadTimer = Timer()
loadTimer.start()

# Connect to MySQL DB
"""
db = database.DB()
db.start()
db.executeScriptFromFile(DB_SETUP_PATH)
db.stop()
"""

# Import Cogs from /cogs directory

print( '------' )
print( "Attempting load of extensions in '/cog' directory...")
allExtensionsLoaded = True
if __name__ == "__main__":
  for file in os.listdir( "./cogs" ):
    if file.endswith( ".py" ):
      extension = file[:-3]
      # Attempt to load extension 
      # Some python files might not have a properly
      # configured setup() method, need to account for that.
      try:
        bot.load_extension( f"cogs.{extension}" )
        print( f"Loaded extension '{extension}'" )
      except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        print( f"Failed to load extension {extension}\n{exception}" )
        allExtensionsLoaded = False 

# Display success / failure on console
if allExtensionsLoaded:
  print("SUCCESS: All extensions in '/cog' directory loaded successfully!")
else:
  print("WARNING: One or more extensions could not be loaded. See above for error output.")
print( '------' )

timeStr = loadTimer.stop()
print(f"LOAD TIME: {timeStr} seconds")

print( '------' )

##############################################
# Events
##############################################

@bot.event
async def on_guild_join( guild ):

  guildID = str(guild.id)

  # Check if Guild is registered on database
  if guildID not in db.keys():
    db[guildID] = {}

  return

@bot.event 
async def on_message( message ):
  """
  Defines behavior for bot on receiving message in chat
  """
  # Ignore messages from self or other bots
  if message.author == bot.user or message.author.bot:
    return
  await bot.process_commands(message)

@bot.event
async def on_ready():
  """
  Defines behavior for bot when ready to execute commands
  """
  # Change status on Discord
  await bot.change_presence(
    activity = discord.Activity(
      type = discord.ActivityType.watching,
      name = 'the sands of time... | !s help' ) )
  # Console output for debugging
  print( '------\nLogged in as' )
  print( bot.user.name )
  print( bot.user.id )
  print( 'https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=0'.format('707346305080361022' ) )
  print( '------' )

@bot.event
async def on_command_completion(ctx):
  """
  Defines behavior for bot whenever a command is completed successfully
  """
  # Console output to note whenever the bot successfully
  # runs a command
  fullCommandName = ctx.command.qualified_name
  split = fullCommandName.split( " " )
  executedCommand = str(split[0])
  print( f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})" )

##############################################
# Other Functions
##############################################

# Flask-related support functions to allow
# 24/7 uptime of bot
@app.route('/')
def hello_world():
  return 'Magic Appetizers not included.'

def start_server():
  app.run( host="0.0.0.0", port = 8080 )
  
##############################################
# Bot / Server Initialization
##############################################

# Starts the Flask server
t = Thread( target = start_server )
t.start()

# Runs the bot for use on Discord
bot.run(os.getenv("TOKEN"))

