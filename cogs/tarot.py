##############################################
# Package Imports
##############################################
import asyncio
import discord
import json
import pytz
import random

from datetime import datetime, timedelta
from discord import Embed, User
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from replit import db
from typing import Iterable

from log import ConsoleLog 

##############################################
# Package Imports
##############################################

MODULE = "TAROT"

CARD_FILE_PATH = "data/card_data.json"
CARD_IMAGE_LINK = "https://i.ibb.co/FxCgHwK/cards-fortune-future-moon-star-tarot-tarot-card-1-512.webp"
READ_TAG = 'r'

SERVER_ID = "703015465076785263"

##############################################
# Tarot Cog
##############################################

class Tarot( commands.Cog, name = "Tarot" ):

  def __init__( self,  bot: Bot ):
    self.bot = bot 
    self.logging = ConsoleLog()
    self.loadCardData()

  ##############################################
  # Tarot Cog Events 
  ##############################################
  @tasks.loop( hours = 24 )
  async def dailyTarotReading( self, guild_id: str, user_id: str ) -> None:

    """
    Sends me a daily tarot reading. Will be adapted
    to allow any user to subscribe for one. 
    """

    await self.beforeDailyTarotReading( guild_id, user_id )

    guild = await self.bot.fetch_guild(guild_id)
    user = await guild.fetch_member( user_id )

    await user.send( f"How have you been {user}? I've got your daily tarot reading ready to go! Take a look: " )

    question = "This spread is useful at the beginning of each day in order to find focus and direction. Even though you may have limited time, these three cards can give you practical insights you can start thinking about immediately.\n\n**1.** What will guide me?\n**2.** What will I experience?\n**3.** What must I learn?"

    numCards = 3

    deck = self.card_list.copy()
    random.shuffle( deck )
    cards = self.drawCardsFromList( deck, numCards )

    embed = self.createCardsEmbed( user, cards, question )

    await user.send( embed = embed )

    return 

  async def beforeDailyTarotReading( self, guild_id: str, user_id: str ) -> None:

    tarot_events = db[guild_id]["events"]["tarot"]
    userdata = None

    guild = await self.bot.fetch_guild(guild_id)
    user = await guild.fetch_member( user_id )

    for event in tarot_events:
      if event["user_id"] == user_id:
        userdata = event 

    eventTime = userdata["time"]

    hour = int(eventTime[0:1])
    minute = int(eventTime[3:4])

    now = datetime.now()
    future = datetime(now.year, now.month, now.day, hour, minute)
    if now.hour >= hour and now.minute > minute:
        future += timedelta(days=1)
    delta = (future - now).seconds
    hour, minute = delta // 3600, (delta % 3600) // 60

    self.logging.send( MODULE, f"Scheduled daily tarot message for '{user}' at {eventTime} server time." )

    await asyncio.sleep(delta)

    return

  @commands.Cog.listener()
  async def on_ready( self ):
   
    keys = db[SERVER_ID].keys()
    if "events" not in keys:
      db[SERVER_ID]["events"] = {
        "tarot" : []
      }

    tarot_events = db[SERVER_ID]["events"]["tarot"]

    for event in tarot_events:
      userID = event["user_id"]
      self.dailyTarotReading.start( SERVER_ID, userID )

    return 

  def addEventToDB( self, ctx ):

    newEvent = {}
    # Get User ID
    newEvent["user_id"] = str(ctx.message.author.id)

    # Calculate server time equivalent
    server_time = datetime.now()
      # Get Time of Message Indicated
    user_time = ctx.message.timestamp()
      # Get Server Time 

    # Add event to db[SERVER_ID]["events"]["tarot"]

  ##############################################
  # Tarot Cog Commands
  ##############################################

  @commands.group( name = "tarot" )
  async def tarot( self, ctx: Context ) -> None: 
    if ctx.invoked_subcommand is None:
      await ctx.send("ERROR: Tarot command(s) improperly invoked. Please see '!help' for a list of commands and usage examples.")
    return

  @tarot.command( name = "draw" )
  async def drawCards( self, ctx: Context, *args ) -> None:
    """
    Allows the user to draw a number card from a tarot deck. The user can draw anywhere from 1 to 25 cards at a time.
    """
    await self.bot.wait_until_ready()

    # ERROR CASE: If not enough arguments 
    if len(args) <= 0:
      await ctx.send("ERROR: Not enough arguments to execute command. Please try using the command like so: `!tarot draw <number>`")
      return

    # ERROR CASE: If arguments don't make sense 
    try:
      numCards = int(args[0])
      if numCards < 1 or numCards > 25:
        await ctx.send("ERROR: Number of cards given is out of bounds. Please try with a number between 1 and 25.")
        return
    except Exception as e:
      exception = f"{type(e).__name__}: {e}"
      await ctx.send("ERROR: Not valid input. Consider using the command like this: `!tarot draw <number>`. Keep in mind the module **can only support up to 25 cards** drawn at a time.")
      self.logging.send( MODULE, f"ERROR: Can't parse command input for 'draw': {exception}")
      return

    await ctx.send("What is the question you would like to ask to the cards?")
    msg = await self.bot.wait_for("message")
    question = msg.content

    # Shuffle the cards
    await ctx.send( "Shuffling my deck...")

    deck = self.card_list.copy()
    random.shuffle(deck)

    # Roll for each card indicated 
    await ctx.send( f"Drawing `{numCards}` card(s)...")

    cards = self.drawCardsFromList( deck, numCards )

    user = ctx.message.author

    # Create embed
    embed = self.createCardsEmbed( user, cards, question )
    
    # Send embed to chat
    await ctx.send( embed = embed )

    return

  ##############################################
  # Tarot Cog Support Functions
  ##############################################

  # Synchronous Support Functions

  def createCardsEmbed( self, user: User, cardLst: Iterable[list], question: str ) -> Embed:
    """
    Support functions for '!tarot draw'. Creates the card embed and returns it for sending.
    """
    # Get user from context 

    # Create embed 
    embed = discord.Embed(
      title = f"Tarot Reading",
      description = f"**Question:** {question}",
      color = discord.Color.purple(),
      timestamp = datetime.now() )
    embed.set_author(
      name = str(user),
      icon_url = str(user.avatar_url)
    )
    embed.set_thumbnail( url = CARD_IMAGE_LINK )

    # Add fields iteratively 
    count = 1
    for card in cardLst:
      cardName = card["name"]
      cardStr = f"{count}. {cardName}"

      reversed = random.randint( 0, 1 )
      if reversed == 0:
        meaning_key = "meaning_rev"
        cardStr += " (R) [NO]"
      else:
        meaning_key = "meaning_up"
        cardStr += " [YES]"

      cardDesc = card[meaning_key]

      embed.add_field(
        name = cardStr,
        inline = False,
        value = cardDesc
      )
      count += 1

    return embed
    
  def drawCardsFromList( self , deck: Iterable[list], numCards: int ) -> Iterable[list]:
    """
    Support function for '!tarot draw'. Pulls a specified number of items from the given 'deck'.
    """
    cards = []
    iterations = 0

    # For the number of cards needed (or while we're there)
    # While loop used to not worry about length of deck
    while iterations < numCards:
      # If we only need one card, top deck 
      if numCards == 1:
        roll = 0
      else:
        # Roll for whatever card in the deck
        roll = random.randint( 0, len(deck) - 1)
      # Remove card from deck
      card = deck.pop( roll )
      # Add card to drawn list
      cards.append( card )
      iterations += 1

    # Return cards back to the user
    return cards

  def loadCardData( self ) -> None:
    """
    Support function for Tarot Cog. Loads the card list into memory on bot startup. 
    """
    self.logging.send( MODULE, "> Loading card list...")

    # Open card list file and set card_list var to json result
    try:
      with open( CARD_FILE_PATH, READ_TAG ) as read_file:
        self.card_list = json.load(read_file)
        self.card_list = self.card_list["cards"]
      self.logging.send( MODULE, "> Card list loaded successfully!")

    # Print out what went wrong on startup
    except Exception as e:
      exception = f"{type(e).__name__}: {e}"
      self.logging.send( MODULE, 
        f"> ERROR: Failed to load card lists. \n{exception}" )
      self.logging.send( MODULE,
        "WARNING: Tarot module may not work as intended. See error output for more details." )

    return

  # End of Tarot Cog 

##############################################
# Setup Function for Bot
##############################################

def setup( bot: Bot ) -> None:
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( Tarot( bot ) )
