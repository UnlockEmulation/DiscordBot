'''
what this page does:
Holds all commands related to music controls

TODO: Add queuing system

'''
import asyncio
import discord
import youtube_dl
from discord.ext import commands

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music (commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.queuePos = 0

    @commands.command(help="Has the bot join the Voice Channel that you're in")
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel!")
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()
    
    @commands.command(help="Immediately plays the given song, bypassing and clearing the queue")
    async def play(self, ctx, *, url):
        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                await ctx.message.delete()
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.send(f'Now playing: {player.title}')
        except:
            await ctx.send('Something went wrong - Please try again later')

    @commands.command(hidden=True)
    async def test(self, ctx, *, url):

        

        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                if len(self.queue) == 0:
                    await self.checkQueue(ctx.voice_client, player)
                    await ctx.send(f'Now playing: {player.title}')
                else:
                    self.queue.append(player)
                    await ctx.send(f'Added {player.title} to the queue')
                    print(self.queue)
        except Exception as e:
            await ctx.send(f"Something went wrong - Please try again later - Error: {e}")

    @commands.command(hidden=True)
    async def inVoice(self, ctx):
        await ctx.message.delete()
        if ctx.voice.is_playing():
            await ctx.send("Yes")
        else:
            await ctx.send("No")

    async def checkQueue(self, ctx, id):
        if self.queue[id] != []:
            voice = ctx.guild.voice_client
            source = self.queue[id].pop(0)
            voice.play(source, after=lambda x=0: self.checkQueue(ctx, ctx.message.guild.id))
        else:
            await ctx.send('There is nothing in the Queue')

    @commands.command(help="NOT WORKING -- Goes to the next song in the queue")
    async def skip(self, ctx):
        self.queuePos += 1
        ctx.voice_client.play(self.queue[self.queuePos], after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Skipping')

    @commands.command(help="NOT WORKING -- Clears the queue")
    async def clear(self, ctx):
        self.queue = []
        self.queuePos = 0
        try:
            await ctx.voice_client.disconnect()
        except:
            pass
        await ctx.send('Queue cleared')

    @commands.command(help="NOT WORKING -- displays the queue")
    async def queue(self, ctx):
        i = 0
        response = ''
        if len(self.queue) > 0:
            while i < len(self.queue):
                player = self.queue[i]
                i += 1
                response = response + f'{i}. {player.title}\n'
            await ctx.send(response)
        else:
            await ctx.send('There is nothing in the queue')
    
    @commands.command(help="Stops music playback and clears the queue")
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
        self.queue = []
        self.queuePos = 0

    @commands.command(help="Pauses music playback")
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send("Paused")

    @commands.command(help="Resumes music playback")
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send("Resumed")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if not member.id == self.bot.user.id:
            return
        elif before.channel is None:
            voice = after.channel.guild.voice_client
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused():
                    time = 0
                if time == 120:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(bot):
    bot.add_cog(Music(bot))
