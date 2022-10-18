"""
What this code will do:
Allows the editing of nicknames and adding/removing of roles for given users

What to add still:


"""

from discord.ext import commands
import discord


class profile_editing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Give someone a new role!', aliases=['ar'])
    async def addRole(self, ctx, user:discord.Member, *, role:discord.Role):
        await user.add_roles(role)
        await ctx.send('Role updated')

    @commands.command(help="Give someone a new nickname!", aliases=['rn'])
    async def rename(self, ctx, user:discord.Member, *, name=None):
        if name != None:
            await user.edit(nick=name)
            await ctx.send('Name updated')
        elif name == None:
            await user.edit(nick=user.username)

def setup(bot):
    bot.add_cog(profile_editing(bot))
