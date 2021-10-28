##############################################
# Package Imports
##############################################
import asyncio
import discord
import json
import pytz
import random

from datetime import datetime, timedelta
from discord import Embed, Guild, User
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from typing import Iterable

import database
from log import ConsoleLog 

##############################################
# Package Imports
##############################################

MODULE = "TAROT"

CARD_FILE_PATH = "data/card_data.json"
CARD_IMAGE_LINK = "https://i.ibb.co/FxCgHwK/cards-fortune-future-moon-star-tarot-tarot-card-1-512.webp"
READ_TAG = 'r'


GET_EVENTS_SCRIPT = """
SELECT server_id, user_id, event_time
FROM events
WHERE category = "tarot";
"""
##############################################
# Tarot Cog
##############################################

class Tarot( commands.Cog, name = "Tarot" ):

  def __init__( self,  bot: Bot ):
    self.bot = bot 
    self.logging = ConsoleLog()
    self.db = database.DB()
    self.loadCardData()
    # self.loadTimezones()
    # self.loadTimezoneEmbed()
    
  @tasks.loop( hours = 24 )
  async def dailyTarotReading( self, tarot_event: Iterable[tuple] ) -> None:
      
      guildID = tarot_event[0]
      guild = await self.bot.fetch_guild(guildID)
      userID = tarot_event[1]
      user = await guild.fetch_member(userID)
      eventTime = tarot_event[2]
      
      await self.beforeDailyTarotReading( guild, user, eventTime )
      
      await user.send(f"How have you been {user}? I've got your daily tarot reading ready to go! Take a look below:")
      
      question = ""
      
      numCards = 3
      
      deck = self.card_list.copy()
      random.shuffle( deck )
      cards = self.drawCardsFromList( deck, numCards )
      
      embed = self.createCardsEmbed( user, cards, question )
      
      await user.send( embed = embed )
      
      return
    
  async def beforeDailyTarotReading( self, guild: Guild, user: User, event_time: str )  -> None:
      
      if event_time[0:1].startswith("0"):
          hour = int(event_time[1])
      else:
          hour = int(event_time[0:1])
      if event_time[3:4].startswith("0"):
            minute = int(event_time[4])
      else:
          minute = int(event_time[3:4])
      
      now = datetime.now()
      future = datetime(now.year, now.month, now.day, hour, minute)
      if now.hour >= hour and now.minute > minute:
          future += timedelta(days=1)
          
      delta = (future - now).seconds
      self.logging.send( MODULE, f"Scheduled daily tarot reading for '{user}' at '{hour}:{minute}' MT." )
      
      await asyncio.sleep(delta)
      
      return
    
  ##############################################
  # Tarot Cog Events
  ##############################################
  @commands.Cog.listener()
  async def on_ready( self ) -> None:
      
      self.db.start()
      self.db.executeScript(GET_EVENTS_SCRIPT)
      results = self.db.cursor.fetchall()
      
      for tarotEvent in results:
        self.dailyTarotReading.start(tarotEvent)
                                          
      self.db.stop()
      return
          
    
  ##############################################

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
    
  @tarot.command( name = "subscribe" , aliases = ["sub"])
  async def subscribeForDailyTarot( self, ctx: Context ):
    
    await self.bot.wait_until_ready()
    
    # ERROR CASE: if they already have a event scheduled
    
    # Continue conversation in DM's
    
    # Ask for Timezone
    
    # Get timezone 
    
    # Ask for Time 
    
    # Convert time from given timezone to MT
    
    # Update DB with information
    
    # Confirm it has been scheduled at a given time! 
    
    return 
    
  @tarot.command( name = "unsubscribe", aliases = ["unsub"])
  async def unsubscribeFromDailyTarot( self, ctx: Context ):
    
    await self.bot.wait_until_ready()
    
    # ERROR CASE: if they don't have an event scheduled
    
    # Confirm they would like to unsubscribe
    
    # If yes, then remove them from the DB
    
    # Confirm they have been removed from the events DB
    
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
    
  def loadTimezones( self ) -> None:
    
    for tz in pytz.common_timezones:
      print(tz)
    
    return 
    
  def loadTimezoneEmbed( self ) -> None:
    
    return

  # End of Tarot Cog 

##############################################
# Setup Function for Bot
##############################################

def setup( bot: Bot ) -> None:
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( Tarot( bot ) )

