'''
What this does:
Holds all the commands related to the points

script is finished unless more are requested
'''
from discord.ext import commands
import discord
import json
from threading import Event
from main import names


class PointTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command for adding/removing/setting points
    @commands.command(help="Adds, removes or sets points for a given user", category='Test')
    async def points(self, ctx, add_remove_set, amount=None, user: discord.Member = None):
        Event().wait(1)
        await ctx.message.delete()
        if amount is None:  # sets amount value to 1 if not indicated by user
            amount = 1
        if user is None:
            user = ctx.message.author  # sets the user to the one who typed the message if not specified
        uid = user.id
        uid = str(uid)
        if uid not in names:
            await ctx.send("That user is not in the Database", delete_after=10)
            pass
        elif uid in names:
            if add_remove_set == "add" or add_remove_set == "Add":
                names[uid] = names[uid] + int(amount)
                result = str(user.mention) + "'s new balance is: " + str(names[uid]) + " points"
                with open("tracker.json", "w") as f:
                    json.dump(names, f, indent=2)
                await ctx.send(result + "\n Changed by " + ctx.message.author.mention)
            elif add_remove_set == "remove" or add_remove_set == "Remove":
                names[uid] = names[uid] - int(amount)
                result = str(user.mention) + "'s new balance is: " + str(names[uid]) + " points"
                with open("tracker.json", "w") as f:
                    json.dump(names, f, indent=2)
                await ctx.send(result + "\n Changed by " + ctx.message.author.mention)
            elif add_remove_set == "set" or add_remove_set == 'Set':
                names[uid] = int(amount)
                result = str(user.mention) + "'s new balance is: " + str(names[uid]) + " points"
                with open("tracker.json", "w") as f:
                    json.dump(names, f, indent=2)
                await ctx.send(result + "\n Changed by " + ctx.message.author.mention)
            else:
                await ctx.send("Something went wrong", delete_after=10)

    # Adds users into the database
    @commands.command(help="Adds a user into the system")
    async def add_user(self, ctx, user: discord.Member):
        Event().wait(1)
        await ctx.message.delete()
        uid = str(user.id)
        if uid not in names:
            names.update({uid: 100})
            with open("tracker.json", "w") as f:
                json.dump(names, f, indent=2)
            print(names)
            response = "User successfully added to the system"  # if the user isn't added yet
        elif uid in names:
            response = "That user is already in the system"  # if the user is already been added
        else:
            response = "Something weird happened"  # Catch for if there isn't a real user specified or something else
        await ctx.send(response, delete_after=10)

    #Tells bot to say something
    @commands.command()
    async def changelog(self, ctx):
        await ctx.send("Andrew no longer has access to the 'ferda' command")

    # Removes users from the database
    @commands.command(help="Removes a user from the system")
    async def remove_user(self, ctx, user: discord.Member):
        Event().wait(1)
        await ctx.message.delete()
        uid = str(user.id)
        if uid in names:
            names.pop(uid)
            with open("tracker.json", "w") as f:
                json.dump(names, f, indent=2)
            print(names)
            response = "User successfully removed"
        elif uid not in names:
            response = "User not found in database"
        else:
            response = "Something weird happened"
        await ctx.send(response, delete_after=5)

    # Shows a specific users point value
    @commands.command(help="Shows a users current point value")
    async def show(self, ctx, user: discord.Member = None):
        Event().wait(1)
        await ctx.message.delete()
        if user is None:
            user = ctx.message.author
        uid = user.id
        uid = str(uid)
        if uid in names:
            result = f'{user.mention}\'s current balance is {names[uid]} points'
        elif str(uid) not in names:
            result = "That user is not in the database"
        else:
            result = "Something weird happened"
        await ctx.send(result, delete_after=20)

    # Shows every users points value
    @commands.command(help="Shows all users + points")
    async def list(self, ctx):
        Event().wait(1)
        await ctx.message.delete()
        i = 1
        response = ""
        for x in names:
            response = response + f'{i}. <@{x}> : {names[x]}\n'
            i += 1
        await ctx.send(str(response))

    '''@commands.command(hidden=True) # not important to fix, debugging feature
    async def find(self, ctx, user: discord.Member):
        Event().wait(1)
        await ctx.send(str(user.id) + '\n' + str(user) + '\n' + str(user.mention))'''

    @commands.command(hidden=True)
    async def test_me(self, ctx, user):
        await ctx.send(f"{user} is the user")


def setup(bot):
    bot.add_cog(PointTracker(bot))
