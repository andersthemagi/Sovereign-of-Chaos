##############################################
# Package Imports
##############################################
import random
import sys

import discord 
from discord.ext import commands
##############################################
# Constants and Setup
##############################################
answers = [
  'It is certain.', 
  'It is decidedly so.',
  'You may rely on it.',
  'Without a doubt.',
  'Yes - definitely.', 
  'As I see, yes.', 
  'Most likely.', 
  'Outlook good.', 
  'Yes.',
  'Signs point to yes.',
  'Reply hazy, try again.', 
  'Ask again later.', 
  'Better not tell you now.',
  'Cannot predict now.',
  'Concentrate and ask again later.', 
  'Don\'t count on it.',
  'My reply is no.',
  'My sources say no.', 
  'Outlook not so good.', 
  'Very doubtful.'
]

HELP_LINK = "https://magicalmusings.github.io/sovereign/"

class General(commands.Cog, name = "General"):

  ##############################################
  # General Cog Initialization
  ##############################################
  def __init__( self, bot ):
    self.bot = bot

  ##############################################
  # General Cog Commands
  ##############################################

  # ADVICE COMMAND
  @commands.command( name = "advice" , 
    aliases = ['a'])
  async def advice( self, ctx, *, question ):
    """
    Ask any question to the bot
    """
    await self.bot.wait_until_ready()
    
    embed = discord.Embed(
      title="**My Answer:**",
      description=
      f"{ answers [ random.randint( 0, len(answers ) ) ] }",
      color=0x42F56C )
    embed.set_footer(
      text=f"Question: { question }" )
    await ctx.send( embed=embed )

  @commands.command( name = "help", aliases = ["h"])
  async def help( self, ctx ):

    await ctx.send("Looks like you need some help getting around. Take a look at this link for how to use my powers to your benefit.")
    await ctx.send( HELP_LINK )
    return

  # PING COMMAND
  @commands.command( name = "ping" )
  async def ping( self, ctx ):
    """
    Diagnostic command to check latency on Bot Commands
    """
    await self.bot.wait_until_ready()

    await ctx.send( "Pong! The crows took {0}ms in reaching you...".format(
    round( self.bot.latency * 1000, 1 ) ) )

  # STATS COMMAND
  @commands.command( name = "stats" )
  async def stats( self, ctx ):
    """
      Diagnostic command to check version of python and discord.py
    """
    await self.bot.wait_until_ready()

    pythonVersion = sys.version
    dpyVersion = discord.__version__
    await ctx.send( f"I'm running on Python {pythonVersion} and discord.py {dpyVersion}! Whatever that means." )

  @commands.command( name = "whack" )
  async def whack( self, ctx, *args ):
    """
    Bailiff, whack his pp!
    """
    await self.bot.wait_until_ready()

    BAILIFF_PP_MP4 = "https://cdn.discordapp.com/attachments/207364433561911297/872878650456944710/6f7336e20b17b139706a821ef03a67d69dc6a29c98a451a7a5726252e4fc59d7_1.mp4"

    if len(args) > 0:
        person = " ".join(args)
        await ctx.send(person + "\n" + BAILIFF_PP_MP4)
    else:
      await ctx.send("You forgot the person for the message, get whacked.")
      await ctx.send(ctx.message.author + "\n" + BAILIFF_PP_MP4)

    return



##############################################
# Setup Command for Bot
##############################################
def setup(bot):
  print("Attempting load of 'general' extension...")
  bot.add_cog( General( bot ) )