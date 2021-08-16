##############################################
# Package Imports
##############################################
"""
d20 Package: Open-Source dice engine for d20 systems. 

https://d20.readthedocs.io/en/latest/start.html
"""
import d20
from discord.ext import commands
##############################################
# Constants and Setup
##############################################
class DiceRoll( commands.Cog, name = "DiceRoll" ):

  def __init__( self, bot ):
    self.bot = bot

  @commands.command( name = "roll", aliases = ["r"])
  async def rollDice( self, ctx, *, rollStr: str = '1d20'):
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
    return await ctx.send(messageStr)

##############################################
# Setup Command for Bot
##############################################
def setup( bot ):
  print("Attempting load of 'diceroll' extension...")
  bot.add_cog( DiceRoll( bot ) )