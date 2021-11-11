
import d20
import datetime
import discord
import time 
from discord_components import DiscordComponents, ComponentsBot, Button
from discord.ext import commands
from discord.ext.commands import Context

from log import ConsoleLog

MODULE = "GAMES"
CURRENCY_SYMBOL = "₡"

ADD_BET_ID = "add_bet_btn"
HOUSE_MULTIPLIER = 1.15
REM_BET_ID = "rem_bet_btn"

class ChoHanGame:
	
	def __init__( self ):
		self.running = False 
		self.pot = 0
		self.evenBets = {}
		self.oddBets = {}
		return
		
	def start( self, minutes = 5 ):
		self.running = True 
		return 
		
	def checkBetExists( self, userID ):
		if userID in self.evenBets or userID in self.oddBets:
			return True 
		return False
		
	def addBet( self, userID, amt, evenBet = True ):
		if self.checkBetExists( userID ):
			return False
		if evenBet:
			self.evenBets[userID] = amt 
		else:
			self.oddBets[userID] = amt
			
		self.pot += amt 
		return True
		
	def editBet( self, userID , amt ):
		if not self.checkBetExists( userID ):
			return False 
			
		if userID in self.evenBets:
			self.evenBets[userID] = amt 
		else:
			self.oddBets[userID] = amt 
			
		return True
		
	def removeBet( self, userID ):
		if not self.checkBetExists( userID ):
			return False 
		if userID in self.evenBets:
			removed = self.evenBets[userID]
			del self.evenBets[userID]
		else:
			removed = self.oddBets[userID]
			del self.oddBets[userID]
			
		self.pot -= removed
		return True
		
	def end( self ):
		self.running = False 
		
		# Add pot to the result data
		data = {}
		data["pot"] = int( self.pot * HOUSE_MULTIPLIER )
		
		# Roll for events or odds
		roll = d20.roll("2d6")
		data["result"] = str(roll)
		
		# Check which side won
		if roll.total % 2 == 0:
			winners = self.evenBets
		else:
			winners = self.oddBets
			
		# Copy winners dictionary to data 
		data["winners"] = dict(winners)
		
		# Determine number of splits of the pot
		if len(winners) > 0: 
			data["share"] = self.pot // len(winners)
		else:
			data["share"] = 0
		
		return data

class Games( commands.Cog, name = "Games" ):
	
	def __init__( self, bot ):
		self.bot = bot
		self.logging = ConsoleLog()
		self.games = {} 
		self.convos = {}
		# Games catalogued in ' "channelID" : GameClass() ' format
		
	@commands.Cog.listener()
	async def on_button_click( self, interaction ):
		
		channelID = interaction.channel.id
		
		if channelID not in self.games:
			return
			
		userID = interaction.user.id
		if userID in self.convos:
			await interaction.user.send("You're already trying to talk with me about something else. Finish that conversation before starting another.")
			return
		else:
			
			self.convos[userID] = interaction.custom_id
		
	@commands.command( name = "chohan" )
	@commands.is_owner()
	async def runChoHan( self, ctx, *args ):
		
		if len(args) < 1:
			await ctx.send("ERROR: Not enough arguments. Try using the command like this:\n```!chohan <minutes>```")
			return
		
		# Initiate ChoHan
		msg = ctx.message
		channelID = msg.channel.id
		
		if channelID in self.games:
			await ctx.send("ERROR: Cho Han game already runnning in this channel. Please have that game finish before initializing another.")
			return
			
		minutes = 0
		try:
			minutes = int(args[0])
		except:
			await ctx.send("ERROR: Minutes not parseable. Consider using a number like 2 or 5 or 25 or something.")
			return 
			
		if minutes < 2 or minutes > 10:
			await ctx.send("ERROR: Not enough minutes. Cho Han games should last between 2 to 10 minutes.")
			return
		
		game = ChoHanGame()
		
		self.games[channelID] = game
		
		# Loop through timer for 2 - 10 minutes
		timeout = time.time() + 60 * minutes
		completeTime = datetime.datetime.now() + datetime.timedelta( minutes = minutes )
		
		embed = self.getChoHanEmbed( minutes )
		buttons = self.getChoHanButtons()
		
		gameMsg = await ctx.send( 
			"Open the game!", 
			embed = embed,
			components = [ buttons ] )
			
		game.start()
		gameRunning = True 
		lastUpdate = None
		while gameRunning:
			
			currentTime = datetime.datetime.now()
			timeRemaining = completeTime - currentTime
			
			minuteSeconds = divmod( timeRemaining.total_seconds(), 60 )
			timeStr = f"{int(minuteSeconds[0]):<2}:{int(minuteSeconds[1]):<2}"
			
			# Check if update is needed
			if lastUpdate is None:
				lastUpdate = currentTime
				await self.updateChoHanEmbed( game, gameMsg, timeStr )
				
			else:
				calcLastUpdate = currentTime - lastUpdate
				if calcLastUpdate.total_seconds() > 1:
					lastUpdate = currentTime
					await self.updateChoHanEmbed( game, gameMsg, timeStr ) 
			
			if timeRemaining.total_seconds() <= 0:
				gameRunning = False 
				
		results = game.end()
		# While the game is running:
			# Allow placing bets
			# Allow removing bets
			
		# Once the timer is over:
			# House contributes 15% to the total pot 
			# Get lists of winning bets 
			# For each user in the list, divide the pot and give them the currency
			# Output the results. 
			# Remove game from list of games 
			
		del self.games[channelID]
			
		return
		
	async def updateChoHanEmbed( self, game, game_msg, timeStr ):
		
		
		embed = game_msg.embeds[0]
		embed_dict = embed.to_dict()
		
		
		for field in embed_dict["fields"]:
			# Update Time on Embed
			if field["name"] == "Time:":
				field["value"] = timeStr
			if field["name"] == "Pot":
				field["value"] = str(game.pot)
			if field["name"] == "Evens:":
				
				valueStr = ""
				line = 0
				if len(game.evenBets) < 1:
					valueStr = "None."
				else:
					for bet in game.evenBets:
						if line != 0:
							valueStr += "\n"
						user = self.bot.fetch_user(bet.key)
						valueStr += f"{user.mention}"
				field["value"] = valueStr
				
		embed = discord.Embed.from_dict(embed_dict)
		await game_msg.edit( embed = embed)
		return
			
		
	def getChoHanEmbed( self, minutes  ):
		embed = discord.Embed(
			title = "Cho Han",
			color = discord.Colour.green()
		)
		embed.timestamp = datetime.datetime.now()
		embed.set_thumbnail( url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimage.flaticon.com%2Ficons%2Fpng%2F512%2F297%2F297558.png&f=1&nofb=1" )
		embed.add_field(
			name = "Status:",
			inline = True,
			value = "IN PROGRESS"
		)
		embed.add_field(
			name = "Time:",
			inline = True,
			value = f"{minutes}:00"
		)
		embed.add_field(
			name = "Pot:",
			inline = False,
			value = f"**{CURRENCY_SYMBOL}** 0"
		)
		embed.add_field(
			name = "Evens:",
			inline = True,
			value = "None."
		)
		embed.add_field(
			name = "Odds:",
			inline = True,
			value = "None."
		)
		
		return embed
		
		
	def getChoHanButtons( self ):
		
		buttons = [] 
		buttons.append(Button( label = "Add Bet", custom_id = ADD_BET_ID, style = "3" ))
		buttons.append(Button( label = "Remove Bet", custom_id = REM_BET_ID, style = "4" ))
		
		return buttons
		
		

def setup( bot ): 
	logging = ConsoleLog()
	logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
	bot.add_cog( Games( bot ) )
