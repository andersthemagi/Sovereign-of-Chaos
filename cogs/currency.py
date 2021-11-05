from discord.ext import commands
from discord.ext.commands import Context

import database
from log import ConsoleLog

MODULE = "CURRENCY"
CURRENCY_SYMBOL = "₡"

ADD_CURRENCY_SCRIPT = """
UPDATE users SET currency = currency + %s WHERE user_id = %s;
"""

ADD_RUNNING_TOTAL_SCRIPT = """
UPDATE users SET total_earned = total_earned + %s WHERE user_id = %s;
"""

CHECK_USER_EXISTS_SCRIPT = """
SELECT * FROM users WHERE user_id = %s;
"""

EDIT_CURRENCY_SCRIPT = """
UPDATE users SET currency = %s WHERE user_id = %s;
"""

GET_BALANCE_SCRIPT = """
SELECT currency , total_earned FROM users WHERE user_id = %s;
"""

SUBTRACT_CURRENCY_SCRIPT = """
UPDATE users SET currency = currency - %s WHERE user_id = %s;
"""

class Currency( commands.Cog, name = "Currency" ):
	
	def __init__( self, bot ):
		self.bot = bot
		self.logging = ConsoleLog()
		self.db = database.DB()
		
	# Expected Implementation:
	
	## Events:
	### - on_message: used for adding currency everytime a user sends a message
	
	@commands.Cog.listener()
	async def on_message( self, message ) -> None:
		
		# ERROR CASE: If the user is a bot
		if message.author == self.bot.user or message.author.bot:
			return
			
		# ERROR CASE: If the user is DMing the bot
		if message.guild == None:
			return
			
		# ERROR CASE: If the user is using a command
		if message.content.startswith( "!" ):
			return
		elif len(message.content) < 2:
			return
			
		user = message.author
		userID = message.author.id
		guild = message.guild 
			
		# Check if user exists in DB  
		self.connectToDB()
		vals = (userID, )
		self.db.executeScript( CHECK_USER_EXISTS_SCRIPT, vals)
		result = self.db.cursor.fetchone()
		
		if result is None:
			self.disconnectFromDB()
			return 
		
		# Add currency to user 
		vals = (1 , userID )
		self.db.executeScript( ADD_CURRENCY_SCRIPT, vals)
		vals = (1, userID )
		self.db.executeScript( ADD_RUNNING_TOTAL_SCRIPT, vals)
		vals = (userID, )
		self.db.executeScript( GET_BALANCE_SCRIPT, vals)
		result = self.db.cursor.fetchone()
		
		balance = result[0]
		runningTotal = result[1]
		self.logging.send( MODULE, f"User {user.display_name} earned 1 currency. Current Balance: {CURRENCY_SYMBOL} {balance} | Running Total: {CURRENCY_SYMBOL} {runningTotal}" )
		
		self.disconnectFromDB()
		return
	
	## Commands: 
	### - money/wallet: used to check how much money without seeing rank info
	### - trade: used to send currency back / forth between users
	
	@commands.command( name = "balance", aliases = ["bal"] )
	async def checkbalance( self, ctx ):
		"""
		Usage: !bal
		"""
		
		# Get balance from table 
		message = ctx.message
		userID = message.author.id
		user = message.author 
		
		self.connectToDB()
		vals = (userID, )
		self.db.executeScript( GET_BALANCE_SCRIPT , vals)
		result = self.db.cursor.fetchone()
		
		balance = result[0]
		runningTotal = result[1]
		
		# Return to user 
		await ctx.send(f"Hi, {user.mention}! You've currently got {CURRENCY_SYMBOL} {balance}. You've earned {CURRENCY_SYMBOL} {runningTotal} on this server to date. ")
		
		self.disconnectFromDB()
		return
		
	@commands.command( name = "trade", aliases = ["t"] )
	async def trade( self, ctx, *args ):
		"""
		Usage: !trade <mention> <amt>
		"""
		
		if len(args) < 2:
			await ctx.send("ERROR: Not enough arguments. Try adjusting your command usage to what's below and try again.\n```!transfer <@mention> <amount>```")
			return
		
		# Check that user has funds 
		try:
			message = ctx.message
			user = message.author
			userID = message.author.id
			
			destination = message.mentions[0].id
			destination_user = await message.guild.fetch_member(destination)
			amt = int(args[1])
		except:
			await ctx.send("ERROR: Something went wrong when attempting to set up the transfer. Try adjusting your command usage to what's below and try again.\n```!transfer <@mention> <amount>```")
			return
		
		self.connectToDB()
		vals = (userID, )
		self.db.executeScript( GET_BALANCE_SCRIPT, vals )
		result = self.db.cursor.fetchone()
		
		balance = int(result[0])
		
		if amt == 0:
			await ctx.send("Why would you want to trade nothing?")
			self.disconnectFromDB()
			return 
		elif amt < 0:
			await ctx.send("...I can't subtract from someone else.")
			self.disconnectFromDB()
			return
					
		if amt > balance:
			await ctx.send(f"Sorry! You only have **{CURRENCY_SYMBOL}** {balance} available. Should I use that value instead (y/n)?")		
				
			acceptingInput = True
			while acceptingInput:
				msg = await self.bot.wait_for("message")
				result = await self.checkYN( ctx, msg, userID )
				if result == "CONTINUE":
					amt = balance
					acceptingInput = False 
				elif result == "STOP":
					await ctx.send("Alright, cancelling this trade.")
					self.disconnectFromDB()
					return
		
		# Confirm transfer
		await ctx.send( f"Confirming: You ({user.mention}) would like to send **{CURRENCY_SYMBOL}** {amt} to {destination_user.mention}? \n**Type 'y' or 'n' to confirm/deny.**" )
		acceptingInput = True
		while acceptingInput:
			msg = await self.bot.wait_for("message")
			result = await self.checkYN( ctx, msg, userID )
			if result == "CONTINUE":
				acceptingInput = False 
			elif result == "STOP":
				await ctx.send("Alright, cancelling this trade.")
				self.disconnectFromDB()
				return	
		
		# Execute transfer
		vals = (amt, userID)
		self.db.executeScript(SUBTRACT_CURRENCY_SCRIPT, vals)
		vals = (amt, destination)
		self.db.executeScript(ADD_CURRENCY_SCRIPT, vals)
		
		if destination != userID:
			vals = (amt, destination)
			self.db.executeScript(ADD_RUNNING_TOTAL_SCRIPT, vals)
			await ctx.send(f"Awesome! {destination_user.mention}, you're now **{CURRENCY_SYMBOL}** {amt} richer!")
		
		else:
			await ctx.send(f"Awesome! {destination_user.mention}, you're now **{CURRENCY_SYMBOL}** {amt} richer! ...or are you..?")
		
		
		self.disconnectFromDB()
		return
	
	## Admin / Owner Commands: 
	### - addcurr: used by addmin to add currency to a user
	### - subcurr: used by admin to subtract currency from a user
	### - editcurr: used by admin to set the currency total to a new value
	### - forcetrade: used by admin to force a trade of funds between users
	
	@commands.command( name = "addcurr")
	@commands.is_owner()
	async def addCurrency( self, ctx, *args ):
		"""
		Usage: !addcurr <mention> <amt>
		"""
		# Add currency to a users record
		if len(args) < 2:
			await ctx.send("ERROR: Not enough arguments. Try adjusting your command usage to what's below and try again.\n```!addcurr <mention> <amount>```")
			return
		
		# Check that user has funds 
		try:
			message = ctx.message
			
			destination = message.mentions[0].id
			destination_user = await message.guild.fetch_member(destination)
			amt = int(args[1])
		except:
			await ctx.send("ERROR: Something went wrong when attempting to set up the transfer. Try adjusting your command usage to what's below and try again.\n```!addcurr <mention> <amount>```")
			return
		
		if amt == 0:
			await ctx.send("Why would you want to trade nothing?")
			self.disconnectFromDB()
			return 
		elif amt < 0:
			await ctx.send("...I can't subtract from someone else.")
			self.disconnectFromDB()
			return
			
		self.connectToDB()
		
		# Execute transfer
		vals = (amt, destination)
		self.db.executeScript(ADD_CURRENCY_SCRIPT, vals)
		
		vals = (amt, destination)
		self.db.executeScript(ADD_RUNNING_TOTAL_SCRIPT, vals)
		await ctx.send(f"User {destination_user.mention} has been given **{CURRENCY_SYMBOL}** {amt}.")
		

		self.disconnectFromDB()
		# Output success
		return
		
	@commands.command( name = "subcurr")
	@commands.is_owner()
	async def subtractCurrency( self, ctx, *args ):
		"""
		Usage: !subcurr <mention> <amt>
		"""
		# Subtract currency from a users record
		if len(args) < 2:
			await ctx.send("ERROR: Not enough arguments. Try adjusting your command usage to what's below and try again.\n```!subcurr <mention> <amount>```")
			return
		
		# Check that user has funds 
		try:
			message = ctx.message
			
			destination = message.mentions[0].id
			destination_user = await message.guild.fetch_member(destination)
			amt = int(args[1])
		except:
			await ctx.send("ERROR: Something went wrong when attempting to set up the transfer. Try adjusting your command usage to what's below and try again.\n```!subcurr <mention> <amount>```")
			return
		
		if amt == 0:
			await ctx.send("Why would you want to trade nothing?")
			self.disconnectFromDB()
			return 
		elif amt < 0:
			await ctx.send("...I can't subtract from someone else.")
			self.disconnectFromDB()
			return
			
		self.connectToDB()
		
		# Execute transfer
		vals = (amt, destination)
		self.db.executeScript(SUBTRACT_CURRENCY_SCRIPT, vals)
		
		await ctx.send(f"**{CURRENCY_SYMBOL}** {amt} has been taken from {destination_user.mention}.")

		self.disconnectFromDB()
		# Output success
		return
		
	@commands.command( name = "editcurr")
	@commands.is_owner()
	async def editCurrency( self, ctx, *args ):
		"""
		Usage: !editcurr <mention> <amt>
		"""
		# Set a users currency value 
		if len(args) < 2:
			await ctx.send("ERROR: Not enough arguments. Try adjusting your command usage to what's below and try again.\n```!editcurr <mention> <amount>```")
			return
		
		# Check that user has funds 
		try:
			message = ctx.message
			
			destination = message.mentions[0].id
			destination_user = await message.guild.fetch_member(destination)
			amt = int(args[1])
		except:
			await ctx.send("ERROR: Something went wrong when attempting to set up the transfer. Try adjusting your command usage to what's below and try again.\n```!editcurr <mention> <amount>```")
			return
		
		if amt == 0:
			await ctx.send("Why would you want to trade nothing?")
			self.disconnectFromDB()
			return 
		elif amt < 0:
			await ctx.send("...I can't subtract from someone else.")
			self.disconnectFromDB()
			return
			
		self.connectToDB()
			
		# Get User Balance
		vals = (destination, )
		self.db.executeScript(GET_BALANCE_SCRIPT, vals)
		result = self.db.cursor.fetchone()
		
		bal = int(result[1])
		totaladj = amt - bal
		
		if totaladj <= 0:
			totaladj = 0
		
		# Execute transfer
		vals = (amt, destination)
		self.db.executeScript(EDIT_CURRENCY_SCRIPT, vals)
		
		# Adjust total earned
		vals = (totaladj, destination)
		self.db.executeScript(ADD_RUNNING_TOTAL_SCRIPT, vals)
		
		
		await ctx.send(f"{destination_user.mention} balance adjusted from **{CURRENCY_SYMBOL}** {bal} to **{CURRENCY_SYMBOL}** {amt}.")

		self.disconnectFromDB()
		# Output success
		return
		
	@commands.command( name = "forcetrade", aliases = ["ft"])
	@commands.is_owner()
	async def forceTrade( self, ctx, *args ):
		"""
		Usage: !ft <from_mention> <to_mention> <amt>
		"""
		if len(args) < 3:
			await ctx.send("ERROR: Not enough arguments. Try adjusting your command usage to what's below and try again.\n```!ft <@from_mention> <@to_mention> <amount>```")
			return
		
		# Check that user has funds 
		try:
			message = ctx.message
			userID = message.mentions[0].id
			user = await message.guild.fetch_member(userID)
			
			if len(message.mentions) < 2:
				destination = message.mentions[0].id
			else:
				destination = message.mentions[1].id
			destination_user = await message.guild.fetch_member(destination)
			amt = int(args[2])
		except:
			await ctx.send("ERROR: Something went wrong when attempting to set up the transfer. Try adjusting your command usage to what's below and try again.\n```!ft <@from_mention> <@to_mention> <amount>```")
			return
		
		self.connectToDB()
		vals = (userID, )
		self.db.executeScript( GET_BALANCE_SCRIPT, vals )
		result = self.db.cursor.fetchone()
		
		balance = int(result[0])
		
		if amt == 0:
			await ctx.send("Why would you want to trade nothing?")
			self.disconnectFromDB()
			return 
		elif amt < 0:
			await ctx.send("...I can't subtract from someone else.")
			self.disconnectFromDB()
			return
					
		if amt > balance:
			await ctx.send("Invalid amount. Transfer amount must be less than current balance.")
			self.disconnectFromDB()
			return
		
		# Execute transfer
		vals = (amt, userID)
		self.db.executeScript(SUBTRACT_CURRENCY_SCRIPT, vals)
		vals = (amt, destination)
		self.db.executeScript(ADD_CURRENCY_SCRIPT, vals)
		
		if destination != userID:
			vals = (amt, destination)
			self.db.executeScript(ADD_RUNNING_TOTAL_SCRIPT, vals)
			await ctx.send(f"User {destination_user.mention} has been force transferred **{CURRENCY_SYMBOL}** {amt} from {user.mention}.")
		
		else:
			await ctx.send(f"User {destination_user.mention} has been force transferred **{CURRENCY_SYMBOL}** {amt} from {user.mention}.")
		
		self.disconnectFromDB()
		return
	
	## Other
	### - Currently N/A.
	
	async def checkYN( self, ctx, msg , userID ):
		if msg.author == self.bot.user or msg.author.bot:
			return "IGNORE"
			
		if msg.content == "y" and msg.author.id == userID:
			return "CONTINUE"
			
		elif msg.content == "n" and msg.author.id == userID:
			return "STOP"
			
		else:
			await ctx.send("That doesn't look like 'y' or 'n'. Try again.")
			return "IGNORE"	
	
	def connectToDB( self ) -> None:
		if not self.db.openDB:
			self.db.start()
		return 
    
	def disconnectFromDB( self ) -> None:
		if self.db.openDB:
			self.db.stop()
		return
		
		
def setup( bot ):
	logging = ConsoleLog()
	logging.send( MODULE, f"Attempting load of '{MODULE}' extension...")
	bot.add_cog( Currency( bot ) )
