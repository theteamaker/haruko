from discord.ext import commands
from cogs.configuration import get_prefix
from env import HARUKO_TOKEN

bot = commands.Bot(command_prefix=get_prefix)
COGS = ['tracking']

for cog in COGS:
    bot.load_extension(f"cogs.{cog}")

@bot.event
async def on_ready():
    print(f"Bot has logged in as {bot.user}!")

bot.run(HARUKO_TOKEN)