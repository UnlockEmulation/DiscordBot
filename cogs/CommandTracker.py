from discord.ext import commands
from datetime import datetime


class CommandTracker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_command')
    async def print(self, ctx):
        date = datetime.now()
        server = ctx.guild.name
        user = ctx.author
        command = ctx.message.content
        commandhistory = f'{server} > {user} > {command}'
        wholedate = date.strftime("%B %d %Y - %H:%M:%S") # yy-MM-dd HH:mm:ss
        history = open('Command History.txt', 'a')
        history.write(wholedate + ": " + commandhistory + "\n")
        history.close()


def setup(bot):
    bot.add_cog(CommandTracker(bot))
