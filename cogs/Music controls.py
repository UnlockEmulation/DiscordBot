'''
what this page does:
Holds all commands related to music controls

TODO: Add searching for music though youtube
TODO: Add playing songs in a voice channel
TODO: Add queuing system

'''


from discord.ext import commands
import discord
import youtube_dl

class music (commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(music(bot))
