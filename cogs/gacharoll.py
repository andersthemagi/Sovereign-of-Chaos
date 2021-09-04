##############################################
# Package Imports
##############################################
import discord
import json 
from discord.ext import commands
from discord.ext.commands import Bot, Context
from random import randint
from typing import Iterable

from log import ConsoleLog

##############################################
# Constants and Setup
##############################################
MODULE = "GACHAROLL"
READ_TAG = "r"

class GachaRoll( commands.Cog, name = "gacharoll" ):

  ##############################################
  # GachaRoll Cog Initialization
  ##############################################
  def __init__( self, bot: Bot ):

    self.bot = bot
    self.logging = ConsoleLog()

    # Gacha Roll Data
    self.UNCOMMON_ITEMS = {}
    self.UNCOMMON_ITEMS_PATH = "data/uncommon.json"
    self.RARE_ITEMS = {}
    self.RARE_ITEMS_PATH = "data/rare.json"
    self.R_COLOR = discord.Color.blue()
    self.VERYRARE_ITEMS = {}
    self.VERYRARE_ITEMS_PATH = "data/veryrare.json"
    self.VR_COLOR = discord.Color.purple()

    self.loadGachaItemLists()

  ##############################################
  # GachaRoll Cog Commands
  ##############################################
  @commands.group( name = "gacharoll", aliases = ["gr"] )
  async def gacharoll( self, ctx: Context ) -> None: 
    if ctx.invoked_subcommand is None:
      await ctx.send("ERROR: GachaRoll command(s) improperly invoked. Please see '!help' for a list of commands and usage examples.")
    return

  @gacharoll.command( name = "uncommon", aliases = ["UC", "uc"])
  async def rollUncommon( self, ctx: Context ) -> None:
    """
    Generates a random 'uncommon' item from the associated .json file. 
    """
    # NOTE: Process for random item generation is very
    # similar, so only the uncommon method is outlined

    await self.bot.wait_until_ready()

    await self.rollForItem( ctx, "uncommon" )

    return

  @gacharoll.command( name = "rare", aliases = ["R", "r"])
  async def rollRare( self, ctx: Context, arg = None ) -> None:
    """
    Generates a random 'rare' item from the associated .json file. 
    """

    await self.bot.wait_until_ready()

    await self.rollForItem( ctx, "rare", self.R_COLOR )

    return

  @gacharoll.command( name = "veryrare", aliases = ["VR", "vr"])
  async def rollVeryRare( self, ctx: Context , arg = None ) -> None:
    """
    Generates a random 'very rare' item from the associated .json file. 
    """

    await self.bot.wait_until_ready()

    await self.rollForItem( ctx, "veryrare", self.VR_COLOR )

    return

  ##############################################
  # GachaRoll Cog Support Functions
  ##############################################

  # ASYNC SUPPORT FUNCTIONS 

  async def displayGachaItemEmbed( self, ctx: Context, 
    item: Iterable[list] , color: discord.Color ) -> None :

    """
    Displays an embed of a given Magical Item
    """

    # Get Item Data 
    item_name = item["name"]
    item_attn = item["attn"]
    item_desc = item["desc"]

    # Prep Item Embed
    embed = discord.Embed(
      title = item_name,
      color = color )
    embed.add_field(
      name = "Requires Attunement?",
      value = item_attn,
      inline = False )
    embed.add_field(
      name = "Description",
      value = item_desc,
      inline = False
    )

    # Send Embed to User
    await ctx.send( embed = embed )
    return 

  async def rollForItem( self, ctx: Context, name: str, 
    color: discord.Color = discord.Color.green() ) -> None:
    """
    Given a string, finds the corresponding item list and
    calls the display embed function. Color corresponds to
    rarity of the item.
    """
    if name == "uncommon":
      items = self.UNCOMMON_ITEMS[name]
    elif name == "rare":
      items = self.RARE_ITEMS[name]
    elif name == "veryrare":
      items = self.VERYRARE_ITEMS[name]

    total_items = len(items)

    await ctx.send(f"Rolling for {total_items} potential items...")
    roll = randint( 1, total_items)
    await ctx.send(f"Pulled {roll}! Grabbing item from the archives...")

    item = items[str(roll)]

    await self.displayGachaItemEmbed( ctx, item, color )

    return

  # SYNCHRONOUS SUPPORT FUNCTIONS 

  def loadGachaItemLists( self ) -> None:
    """
    Attempts to load all .json format item lists from the /data directory
    """
    self.logging.send( MODULE, "> Loading Gacha Item Lists..." )
    allListsLoaded = True

    ITEM_PATHS = [
      self.UNCOMMON_ITEMS_PATH, self.RARE_ITEMS_PATH,
      self.VERYRARE_ITEMS_PATH
    ]
    ITEM_NAMES = [
      "UNCOMMON", "RARE", "VERYRARE"
    ]

    for itempath in ITEM_PATHS:
      index = ITEM_PATHS.index( itempath )
      itemname = ITEM_NAMES[index]
      try:
        with open( itempath, READ_TAG ) as read_file:
          lst = json.load( read_file )
          if itemname == "UNCOMMON":
            self.UNCOMMON_ITEMS = lst
          elif itemname == "RARE":
            self.RARE_ITEMS = lst
          elif itemname == "VERYRARE":
            self.VERYRARE_ITEMS = lst
        self.logging.send( MODULE, f" - {itemname} Item List loaded successfully!" )
      except Exception as e:
        allListsLoaded = False 
        exception = f"{type(e).__name__}: {e}"
        self.logging.send( MODULE, f" - ERROR: Failed to load '{itemname}' item list\n{exception}")

    if allListsLoaded:
      self.logging.send( MODULE, "> All Gacha Items Lists loaded successfully!")
    else:
      self.logging.send( MODULE, "> WARNING: One or more Gacha Item Lists could not be loaded. See above for error output.")
    
    return

##############################################
# Setup Command for Bot
##############################################
def setup( bot : Bot ) -> None:
  logging = ConsoleLog()
  logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
  bot.add_cog( GachaRoll( bot ) )