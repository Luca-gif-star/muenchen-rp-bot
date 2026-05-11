import discord
from discord.ext import commands
from discord import app_commands
from database import add_count, get_count

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_counter = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        # Check if in counting channel (customize as needed)
        if message.channel.name != "counting":
            return
        
        try:
            number = int(message.content.strip())
        except ValueError:
            return
        
        # Get last number
        last_count = get_count(message.author.id)
        
        # Check if number is correct
        if number != last_count + 1:
            await message.add_reaction('❌')
            await message.reply(f"❌ Falsch! Die nächste Zahl sollte {last_count + 1} sein!")
            return
        
        # Check if same person counted twice
        if self.last_counter == message.author.id:
            await message.add_reaction('❌')
            await message.reply(f"❌ Du kannst nicht zwei Mal hintereinander zählen!")
            return
        
        # Add count
        add_count(message.author.id, number)
        self.last_counter = message.author.id
        await message.add_reaction('✅')

    @app_commands.command(name="count", description="Zeige deine aktuelle Counting Statistik")
    async def count_stats(self, interaction: discord.Interaction):
        user_count = get_count(interaction.user.id)
        
        embed = discord.Embed(
            title="📊 Deine Counting Statistik",
            description=f"Gesamt gezählte Zahlen: **{user_count}**",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Nutzer: {interaction.user}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Counting(bot))
