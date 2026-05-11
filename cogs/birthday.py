import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import add_birthday, get_connection
from datetime import datetime

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthdays.start()

    @app_commands.command(name="birthday", description="Registriere deinen Geburtstag")
    @app_commands.describe(date="Dein Geburtstag (DD.MM.YYYY)")
    async def set_birthday(self, interaction: discord.Interaction, date: str):
        try:
            datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            await interaction.response.send_message("❌ Falsches Format! Nutze: DD.MM.YYYY", ephemeral=True)
            return
        
        add_birthday(interaction.user.id, date)
        
        embed = discord.Embed(
            title="🎂 Geburtstag gespeichert",
            description=f"Dein Geburtstag: **{date}**",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        """Check for birthdays daily"""
        conn = get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%d.%m")
        
        cursor.execute('SELECT user_id FROM birthdays WHERE birthday LIKE ?', (f'%{today}%',))
        birthday_users = cursor.fetchall()
        conn.close()
        
        for (user_id,) in birthday_users:
            guild = self.bot.get_guild(next(iter(self.bot.guilds)).id)
            member = guild.get_member(user_id)
            
            if member:
                # Send birthday message
                channel = guild.system_channel or guild.text_channels[0]
                embed = discord.Embed(
                    title="🎂 Alles Gute zum Geburtstag!",
                    description=f"Herzlichen Glückwunsch {member.mention}!",
                    color=discord.Color.gold()
                )
                await channel.send(embed=embed)

    @check_birthdays.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Birthday(bot))
