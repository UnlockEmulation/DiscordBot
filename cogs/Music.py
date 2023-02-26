import discord
from discord.ext import commands
import youtube_dl
import asyncio


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlist = []
        self.current_song = None
        self.voice_client = None

    async def play_next_song(self):
        if self.playlist:
            if not self.playlist:
                self.audio.cancel()
            self.voice_client.play(self.playlist[0])
            self.current_song = self.playlist.pop(0)

    async def audio_player_task(self):
        while True:
            if self.voice_client.is_playing():
                await asyncio.sleep(1)
            elif self.voice_client.is_paused():
                await asyncio.sleep(1)
            else:
                await self.play_next_song()

    @commands.command()
    async def play(self, ctx, *, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        self.playlist.append(player)
        await ctx.send(f'Now playing: {player.title}')
        '''self.audio = self.bot.loop.create_task(self.audio_player_task())'''

    @commands.command()
    async def playlist(self, ctx, *, url=None):
        if url is None:
            # Display the current playlist
            if not self.playlist:
                await ctx.send("The playlist is empty.")
            else:
                playlist_str = "\n".join(self.playlist)
                await ctx.message.delete()
                await ctx.send(f"Current playlist:\n{playlist_str}")
        else:
            # Add the URL to the playlist
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            self.playlist.append(player)
            await ctx.send(f"Added {player.title} to the playlist.")

    @commands.command(help="Stops music playback and clears the queue")
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
        self.playlist = []

    @play.before_invoke
    async def ensure_voice(self, ctx):
        """Joins a voice channel if the bot is not already in one"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                self.voice_client = await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


# set up youtube_dl options
ydl_opts = {
    'format': 'bestaudio/best',
    'default_search': 'auto'
}

ffmpeg_options = {
    'options': '-vn'
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(ydl_opts).extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def setup(bot):
    bot.add_cog(Music(bot))
