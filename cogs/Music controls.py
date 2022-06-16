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

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Join a VC to play music from")
        voiceChannel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voiceChannel.connect()
        else:
            await ctx.voice_client.move_to(voiceChannel)
    
    @commands.command()
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, url : str):
        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max_5', 'options': '-vn'}
        YDL_OPTIONS = {'format':'bestaudio'}
        vc = ctx.voice_client
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source)

    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send("Paused")

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("Resumed")

def setup(bot):
    bot.add_cog(music(bot))
