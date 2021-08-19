##############################################
# Package Imports
##############################################
import discord
import json 
from discord.ext import commands
from random import randint

##############################################
# Constants and Setup
##############################################
READ_TAG = "r"

class GachaRoll( commands.Cog, name = "gacharoll"):

  ##############################################
  # GachaRoll Cog Initialization
  ##############################################
  def __init__( self, bot ):

    self.bot = bot

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
  async def gacharoll( self, ctx ): 
    if ctx.invoked_subcommand is None:
      await ctx.send("ERROR: GachaRoll command(s) improperly invoked. Please see '!help' for a list of commands and usage examples.")
    return

  @gacharoll.command( name = "uncommon", aliases = ["UC", "uc"])
  async def rollUncommon( self, ctx, arg = None ):
    """
    Generates a random 'uncommon' item from the associated .json file. 
    """
    # NOTE: Process for random item generation is very
    # similar, so only the uncommon method is outlined

    await self.bot.wait_until_ready()

    # Pull only uncommon items from imported dictionary
    uc_items = self.UNCOMMON_ITEMS['uncommon']
    total_items = len(uc_items)

    # Get Random Number 
    await ctx.send(f"Rolling for {total_items} potential items...")
    roll = randint( 1, total_items)
    await ctx.send(f"Pulled {roll}! Grabbing item from the archives...")

    # Pull item from list
    item = uc_items[str(roll)]

    # Send list to the user
    await self.displayGachaItemEmbed( ctx, item )

    return

  @gacharoll.command( name = "rare", aliases = ["R", "r"])
  async def rollRare( self, ctx, arg = None ):
    """
    Generates a random 'rare' item from the associated .json file. 
    """

    await self.bot.wait_until_ready()

    rare_items = self.RARE_ITEMS['rare']
    total_items = len(rare_items)

    # Get Random Number 
    await ctx.send(f"Rolling for {total_items} potential items...")
    roll = randint( 1, total_items)
    await ctx.send(f"Pulled {roll}! Grabbing item from the archives...")

    item = rare_items[str(roll)]

    await self.displayGachaItemEmbed( ctx, item , self.R_COLOR )

    return

  @gacharoll.command( name = "veryrare", aliases = ["VR", "vr"])
  async def rollVeryRare( self, ctx, arg = None ):
    """
    Generates a random 'very rare' item from the associated .json file. 
    """

    await self.bot.wait_until_ready()

    vr_items = self.VERYRARE_ITEMS['veryrare']
    total_items = len(vr_items)

    # Get Random Number 
    await ctx.send(f"Rolling for {total_items} potential items...")
    roll = randint( 1, total_items)
    await ctx.send(f"Pulled {roll}! Grabbing item from the archives...")

    item = vr_items[str(roll)]

    await self.displayGachaItemEmbed( ctx, item , self.VR_COLOR )

    return

  ##############################################
  # GachaRoll Cog Support Functions
  ##############################################
  # DISPLAY GACHA ITEM EMBED FUNCTION
  async def displayGachaItemEmbed( self, ctx, item , color = discord.Color.green() ):

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

  # LOAD GACHA ITEM LISTS FUNCTION
  def loadGachaItemLists(self):
    """
    Attempts to load all .json format item lists from the /data directory
    """
    print(" - Loading Gacha Item Lists...")
    allListsLoaded = True
    # Uncommon Items
    try:
      with open( self.UNCOMMON_ITEMS_PATH, READ_TAG ) as read_file:
        self.UNCOMMON_ITEMS = json.load( read_file )
      print(" > Uncommon Item List loaded successfully!")
    except Exception as e:
      allListsLoaded = False 
      itemList = "Uncommon"
      exception = f"{type(e).__name__}: {e}"
      print( f" > Failed to load '{itemList}' item list\n{exception}" )
    # Rare Items 
    try:
      with open( self.RARE_ITEMS_PATH, READ_TAG ) as read_file:
        self.RARE_ITEMS = json.load( read_file )
      print(" > Rare Item List loaded successfully!")
    except Exception as e:
      allListsLoaded = False 
      itemList = "Rare"
      exception = f"{type(e).__name__}: {e}"
      print( f" > Failed to load '{itemList}' item list\n{exception}" )
    # Very Rare Items 
    try:
      with open( self.VERYRARE_ITEMS_PATH, READ_TAG ) as read_file:
        self.VERYRARE_ITEMS = json.load( read_file )
      print(" > Very Rare Item List loaded successfully!")
    except Exception as e:
      allListsLoaded = False
      itemList = "Very Rare"
      exception = f"{type(e).__name__}: {e}"
      print( f" > Failed to load '{itemList}' item list\n{exception}" )

    if allListsLoaded:
      print(" - All Gacha Items Lists loaded successfully!")
    else:
      print(" - WARNING: One or more Gacha Item Lists could not be loaded. See above for error output.")
    
    return

##############################################
# Setup Command for Bot
##############################################
def setup( bot ):
  print("Attempting load of 'gacharoll' extension...")
  bot.add_cog( GachaRoll( bot ) )