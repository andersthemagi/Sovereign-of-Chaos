##############################################
# Package Imports
##############################################
"""
d20 Package: Open-Source dice engine for d20 systems. 

https://d20.readthedocs.io/en/latest/start.html
"""
##############################################
# Package Imports
##############################################
import d20
from discord.ext import commands
from discord.ext.commands import Context

from log import ConsoleLog

##############################################
# Constants and Setup
##############################################

MODULE = "DICEROLL"

##############################################
# DiceRoll Cog
##############################################

class DiceRoll( commands.Cog, name = "DiceRoll" ):

  def __init__( self, bot ):
    self.bot = bot
    self.logging = ConsoleLog

  ##############################################
  # DiceRoll Commands
  ##############################################
  @commands.command( name = "deathroll", aliases = ["droll", "dr"] )
  async def deathroll( self, ctx: Context, *, rollStr: str = '10' ) -> None:
    """
    Command simulating deathrolls from WOW. 
    """
    await self.bot.wait_until_ready()
    
    # Check if roll limit is valid
    try:
      rollLimit = int(rollStr)
      if rollLimit > 10000 or rollLimit < 1:
        return await ctx.send("ERROR: Number too large. Please try a number between `1` and `10,000`.")
    except:
      return await ctx.send("ERROR: That wasn't a number. Please try using the command like this:\n```!deathroll <number>```")
      
    # Prep dice roll string
    diceRoll = f"1d{rollLimit}"
    # Parse dice roll
    roll = d20.roll(diceRoll)
  
    # Prep message string for sending
    messageStr = f"{ctx.message.author.mention} :game_die:\n"
    messageStr += str(roll)
    
    # Add clever quips in message if at the limit or at 1
    if roll.total == rollLimit:
      messageStr += "\nAt this rate, I'd ask the other person to pay up already."
    elif roll.total == 1:
      messageStr += "\nAbsolutely horrible luck. Sure hope you weren't betting too much on this."
    
    # Send and end the functionß
    return await ctx.send(messageStr)

  @commands.command( name = "roll", aliases = ["r"])
  async def rollDice( self, ctx: Context, *, rollStr: str = '1d20') -> None:
    """
    Allows the user to roll dice in the discord chat, similar to Avrae.

    Avrae's Dice Rolling functionality found at the Github Link Below:
    https://github.com/avrae/avrae/blob/master/cogs5e/dice.py
    """
    await self.bot.wait_until_ready()
    
    # Easter Egg from Avrae's Dice Interpreter
    if rollStr == '0/0':
      return await ctx.send("What do you expect me to do, destroy the universe?")

    # If the player would like to roll at advantage
    if 'adv' in rollStr:
      rollStr = rollStr.replace('1', '2', 1)
      rollStr = rollStr.replace('adv', 'kh1', 1)

    # If the player would like to roll at disadvantage
    if 'dis' in rollStr:
      rollStr = rollStr.replace('1', '2', 1)
      rollStr = rollStr.replace('dis', 'kl1', 1)
    
    # Parse roll through dice interpreter
    roll = d20.roll(rollStr)

    # Prep message for send through Discord
    messageStr = f"{ctx.message.author.mention} :game_die:\n"
    messageStr += str(roll)

    # Send message
    await ctx.send(messageStr)

    return 

##############################################
# Setup Command for Bot
##############################################
def setup( bot ) -> None:
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( DiceRoll( bot ) )
