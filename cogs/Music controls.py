'''
what this page does:
Holds all commands related to music controls

TODO: Add queuing system

'''
import asyncio
from enum import Enum
import discord
import youtube_dl
from discord.ext import commands

class QueueIsEmpty(commands.CommandError):
    pass

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

class QueueIsEmpty(commands.CommandError):
    pass

class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2

class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty
        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]
    
    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty
        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty
        self.position += 1
        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None
        return self._queue[self.position]

    def set_repeat_mode(self, mode):
        if mode == 'none':
            self.repeat_mode = RepeatMode.NONE
        elif mode == '1':
            self.repeat_mode = RepeatMode.ONE
        elif mode == 'all':
            self.repeat_mode = RepeatMode.ALL

    def empty(self):
        self._queue.clear()
        self.position = 0

class Music (commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.queuePos = 0

    @commands.command()
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
                    await self.startPlaying(ctx.voice_client, player)
                    await ctx.send(f'Now playing: {player.title}')
                else:
                    self.queue.append(player)
                    await ctx.send(f'Added {player.title} to the queue')
        except Exception as e:
            await ctx.send(f"Something went wrong - Please try again later - Error: {e}")

    async def startPlaying(self, voice_client, player):
        self.queue.append(player)
        i = 0
        while i < len(self.queue):
            try:
                voice_client.play(self.queue[i], after=lambda e: print('Player error%s' % e) if e else None)
            except:
                pass
            i += 1

    @commands.command()
    async def skip(self, ctx):
        self.queuePos += 1
        ctx.voice_client.play(self.queue[self.queuePos], after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Skipping')

    @commands.command()
    async def clear(self, ctx):
        self.queue = []
        self.queuePos = 0
        try:
            await ctx.voice_client.disconnect()
        except:
            pass
        await ctx.send('Queue cleared')

    @commands.command()
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
