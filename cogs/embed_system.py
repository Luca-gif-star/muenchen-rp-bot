import discord
from discord.ext import commands
from discord import app_commands
from database import get_connection
import json

class EmbedSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed_create", description="Erstelle ein neues Embed")
    @app_commands.describe(
        title="Embed Titel",
        description="Embed Beschreibung",
        color="Farbe (hex oder rot/grün/blau)",
        name="Speicherername"
    )
    async def create_embed(self, interaction: discord.Interaction, title: str, description: str, color: str = "0x0000ff", name: str = None):
        # Parse color
        try:
            if color.startswith('#'):
                color_int = int(color[1:], 16)
            elif color.startswith('0x'):
                color_int = int(color[2:], 16)
            else:
                color_int = int(color, 16)
        except:
            color_int = 0x0000ff
        
        embed = discord.Embed(title=title, description=description, color=color_int)
        embed.set_footer(text=f"Erstellt von {interaction.user}")
        
        # Save if name provided
        if name:
            embed_data = {
                'title': title,
                'description': description,
                'color': color_int
            }
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO saved_embeds (name, data)
                VALUES (?, ?)
            ''', (name, json.dumps(embed_data)))
            conn.commit()
            conn.close()
            
            await interaction.response.send_message(f"✅ Embed gespeichert als **{name}**!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="embed_send", description="Sende ein gespeichertes Embed")
    @app_commands.describe(name="Name des Embeds")
    async def send_embed(self, interaction: discord.Interaction, name: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM saved_embeds WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            await interaction.response.send_message(f"❌ Embed **{name}** nicht gefunden!", ephemeral=True)
            return
        
        embed_data = json.loads(result[0])
        embed = discord.Embed(
            title=embed_data['title'],
            description=embed_data['description'],
            color=embed_data['color']
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="embed_list", description="Liste alle gespeicherten Embeds")
    async def list_embeds(self, interaction: discord.Interaction):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM saved_embeds')
        embeds = cursor.fetchall()
        conn.close()
        
        if not embeds:
            await interaction.response.send_message("📭 Keine Embeds gespeichert!", ephemeral=True)
            return
        
        embed_list = "\n".join([f"• {e[0]}" for e in embeds])
        
        embed = discord.Embed(
            title="📋 Gespeicherte Embeds",
            description=embed_list,
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedSystem(bot))
