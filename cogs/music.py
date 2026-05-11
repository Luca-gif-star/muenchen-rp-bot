import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
from collections import deque

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()
        self.current_player = None
        self.is_playing = False

    @app_commands.command(name="play", description="Spiele ein Lied ab")
    @app_commands.describe(song="Liedtitel oder YouTube URL")
    async def play(self, interaction: discord.Interaction, song: str):
        await interaction.response.defer()
        
        if not interaction.user.voice:
            await interaction.followup.send("❌ Du musst in einem Voice Channel sein!", ephemeral=True)
            return
        
        # Get voice channel
        channel = interaction.user.voice.channel
        
        # Connect if not already connected
        if not interaction.guild.voice_client:
            try:
                voice_client = await channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ Konnte nicht beitreten: {e}", ephemeral=True)
                return
        else:
            voice_client = interaction.guild.voice_client
        
        # Download song info
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{song}", download=False)
                if not info:
                    await interaction.followup.send("❌ Lied nicht gefunden!", ephemeral=True)
                    return
                
                video = info['entries'][0]
                url = video['url']
                title = video['title']
        except Exception as e:
            await interaction.followup.send(f"❌ Fehler: {e}", ephemeral=True)
            return
        
        # Add to queue
        self.queue.append({'url': url, 'title': title, 'requester': interaction.user})
        
        embed = discord.Embed(
            title="🎵 Zur Warteschlange hinzugefügt",
            description=f"**{title}**\nAngefordert von: {interaction.user.mention}",
            color=discord.Color.purple()
        )
        
        await interaction.followup.send(embed=embed)
        
        # Play if nothing is playing
        if not self.is_playing:
            await self.play_next(interaction)

    @app_commands.command(name="stop", description="Stoppe die Musik")
    async def stop(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Der Bot ist nicht verbunden!", ephemeral=True)
            return
        
        self.queue.clear()
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("⏹️ Musik gestoppt!", ephemeral=True)

    @app_commands.command(name="queue", description="Zeige die aktuelle Warteschlange")
    async def show_queue(self, interaction: discord.Interaction):
        if not self.queue:
            await interaction.response.send_message("📭 Die Warteschlange ist leer!", ephemeral=True)
            return
        
        queue_text = ""
        for i, song in enumerate(self.queue, 1):
            queue_text += f"{i}. {song['title']}\n"
        
        embed = discord.Embed(
            title="🎵 Aktuelle Warteschlange",
            description=queue_text,
            color=discord.Color.purple()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def play_next(self, interaction: discord.Interaction):
        if not self.queue:
            self.is_playing = False
            return
        
        self.is_playing = True
        song = self.queue.popleft()
        
        voice_client = interaction.guild.voice_client
        if not voice_client:
            return
        
        try:
            source = discord.FFmpegPCMAudio(song['url'])
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(interaction), self.bot.loop
            ))
        except Exception as e:
            print(f"Error playing song: {e}")
            await self.play_next(interaction)

async def setup(bot):
    await bot.add_cog(Music(bot))
