
from discord.ext import commands

class SkillChallenge(
  commands.Cog,
  name = "Skill Challenge" ):

  def __init__(self, bot):
    self.bot = bot

def setup( bot ):
  print("Attempting load of 'skillchallenge' extension...")
  bot.add_cog( SkillChallenge( bot ) )