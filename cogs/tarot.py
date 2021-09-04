##############################################
# Package Imports
##############################################
import discord
import json
import random

from datetime import datetime
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Context
from typing import Iterable

from log import ConsoleLog 

##############################################
# Package Imports
##############################################

MODULE = "TAROT"

CARD_FILE_PATH = "data/card_data.json"
CARD_IMAGE_LINK = "https://i.ibb.co/FxCgHwK/cards-fortune-future-moon-star-tarot-tarot-card-1-512.webp"
READ_TAG = 'r'

##############################################
# Tarot Cog
##############################################

class Tarot( commands.Cog, name = "Tarot" ):

  def __init__( self,  bot: Bot ):
    self.bot = bot 
    self.logging = ConsoleLog()
    self.loadCardData()

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

    # Create embed
    embed = self.createCardsEmbed( ctx, cards, question )
    
    # Send embed to chat
    await ctx.send( embed = embed )

    return

  ##############################################
  # Tarot Cog Support Functions
  ##############################################

  # Synchronous Support Functions

  def createCardsEmbed( self, ctx: Context, cardLst: Iterable[list], question: str ) -> Embed:
    """
    Support functions for '!tarot draw'. Creates the card embed and returns it for sending.
    """
    # Get user from context 
    user = ctx.message.author 

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
