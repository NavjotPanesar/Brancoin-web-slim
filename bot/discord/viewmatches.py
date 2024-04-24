

from discord import Message
import discord
import discord.ext
import discord.ext.commands
from models.dbcontainer import DbService
from models.models import Match, User, Guild
from discord.basecommand import BaseCommand
from discord.ext.commands import Bot

class ViewMatches(BaseCommand):
    prefix = "bran viewmatches"
    usage = prefix
    async def process(self, ctx, message: Message, dbservice: DbService):
        if not message.content.startswith(self.prefix):
            return
        
        with dbservice.Session() as session: 
            open_matches = session.query(Match).filter(Match.finished == False).all()
            context: discord.ext.commands.Context = await ctx(message)
            bot: Bot = context.bot
            for open_match in open_matches:
                embedVar = await ViewMatches.generate_embed_for_match(open_match, bot)
                await message.reply(embed=embedVar)

            if len(open_matches) == 0:
                await message.reply("No pending matches")

    @staticmethod
    async def generate_embed_for_match(match: Match, bot: Bot):
        embedVar = discord.Embed(title="ARAM in progress", description=f"id: {match.match_id}", color=0xccccff)
        embedVar.add_field(name="started (UTC)", value=f"{str(match.start_time)}", inline=False)
        embedVar.add_field(name="Players:", value="--------", inline=False)
        for match_player in match.match_players:
            discord_id = match_player.league_user.discord_user.user_id
            discord_user = await bot.fetch_user(discord_id)
            embedVar.add_field(name=str(discord_user.display_name), value=str(match_player.champion), inline=False)
        embedVar.add_field(name="Votes placed: ", value=str(len(match.votes)))
        vote_time_left_seconds = 5*60 - match.get_time_since_start().seconds
        vote_time_left_seconds = vote_time_left_seconds if vote_time_left_seconds >= 0 else 0
        embedVar.add_field(name="Time left to vote: ", value = str(vote_time_left_seconds) + "s")
        return embedVar