import dataset, re
from discord.ext import commands
from env import HARUKO_SERVERS_DB

servers_db = dataset.connect(HARUKO_SERVERS_DB)["servers"]
DEFAULT_PREFIX = "post!"

def setup(bot):
    bot.add_cog(Configuration(bot))

def get_prefix(bot, message):
    server = servers_db.find_one(server_id=message.guild.id)

    if server != None:
        try:
            if type(server["prefix"]) is str:
                return server["prefix"]
        except:
            pass

    return DEFAULT_PREFIX

class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def set_prefix(self, ctx, *args):
        await ctx.trigger_typing()
        usage = "usage: `set_prefix <prefix>`"

        if len(args) != 1:
            await ctx.send(usage)
            return
        
        if re.match(r"^.{,5}$", args[0]) is None:
            await ctx.send("**Error:** The specified prefix for this bot must be *at most* 5 characters, and contain no spaces.")
            return
        
        try:
            servers_db.upsert(dict(server_id=int(ctx.guild.id), prefix=args[0]), ["server_id"])
            await ctx.send(f"The bot's prefix for this server has been successfully set to `{args[0]}`!")
        except:
            await ctx.send(f"An error in setting the prefix has occurred. Contact {self.bot.owner} for help.")