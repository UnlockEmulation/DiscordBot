import discord
from discord.ext import commands
import json
import os
from threading import Event
from discord.ext.commands import CommandNotFound

me = 267588669781573634  # sets my discord ID for quick reference
bot = commands.Bot(command_prefix='!')  # sets the prefix you need to use when calling a command

# gets the point value and corresponding user ID and sets them into a 2D array
with open("tracker.json", "r") as tracker:
    names = json.load(tracker)
    tracker.close()


# Once the bot is ready it sets the "status" of the bot to show it's "Watching !help"
@bot.event
async def on_ready():
    print("Connected to discord as {0.user}".format(bot))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!help"))


# Error catching
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("There was an error", delete_after=5)
        return
    raise error


# Command for loading a cog
@bot.command(hidden=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"Cog '{extension}' loaded")


# Command for unloading a cog
@bot.command(hidden=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"Cog '{extension}' unloaded")


# Command for reloading the cogs
@bot.command(hidden=True)
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.message.delete()


# Shuts down the bot
@bot.command(hidden=True)
async def sd(ctx):
    if ctx.message.author.id == me:
        Event().wait(1)
        await ctx.message.delete()
        message = await ctx.send("Shutting down")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="shutdown"))
        Event().wait(5)
        await message.delete()
        await bot.change_presence(status=discord.Status.offline)
        await bot.close()
    else:
        Event().wait(1)
        await ctx.message.delete()
        await ctx.send("You're not gonna wanna do that one...", delete_after=10)


# Used for debugging certain commands
@bot.command(hidden=True)
async def debug(ctx):
    await ctx.message.delete()
    await ctx.send(ctx.message.author.id)
    if ctx.message.author.id == me:
        x = input("debug: ")
        if x == "test":
            message = await ctx.send("Test message")
            Event().wait(3)
            await message.delete()
    else:
        await ctx.send("No", delete_after=10)


'''@bot.command(help="Test")
async def test(ctx):
    await ctx.message.delete()
    await ctx.send("your message is {} characters long.".format(len(ctx.message.content)), delete_after=5)'''


# loads in the cogs once the file is run
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# replies to messages with ferda in the message
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if 'ferda' in message.content.lower():
        await message.channel.send('FERDA BOIS')
    await bot.process_commands(message)


text_file = open("bot token.txt", "r")
botToken = text_file.read()
bot.run(botToken)
