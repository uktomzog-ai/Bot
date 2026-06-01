import discord
from discord.ext import commands
from discord import app_commands
import os
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── READY ───────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=1291031538116460646))
    print(f"Logged in as {bot.user}")

# ─── WELCOME MESSAGE ─────────────────────
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}! 🎉")

    # Auto role
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)

# ─── SLASH COMMANDS ──────────────────────
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

@bot.tree.command(name="help", description="Show all commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
    embed.add_field(name="General", value="/ping /help", inline=False)
    embed.add_field(name="Moderation", value="/kick /ban /mute", inline=False)
    embed.add_field(name="Music", value="/play /stop /skip", inline=False)
    await interaction.response.send_message(embed=embed)

# ─── MODERATION ──────────────────────────
@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member.mention} was kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member.mention} was banned. Reason: {reason}")

@bot.tree.command(name="mute", description="Timeout a member for 10 minutes")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member):
    duration = discord.utils.utcnow() + discord.timedelta(minutes=10)
    await member.timeout(duration)
    await interaction.response.send_message(f"🔇 {member.mention} muted for 10 minutes.")

# ─── MUSIC ───────────────────────────────
YTDL_OPTIONS = {
    "format": "bestaudio",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "source_address": "0.0.0.0"
}
FFMPEG_OPTIONS = {"options": "-vn"}

@bot.tree.command(name="play", description="Play a song from YouTube")
async def play(interaction: discord.Interaction, search: str):
    await interaction.response.defer()
    if not interaction.user.voice:
        return await interaction.followup.send("Join a voice channel first!")

    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if not vc:
        vc = await channel.connect()

    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
        url = info["entries"][0]["url"]
        title = info["entries"][0]["title"]

    vc.stop()
    vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))
    await interaction.followup.send(f"🎵 Now playing: **{title}**")

@bot.tree.command(name="stop", description="Stop music and leave")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
    await interaction.response.send_message("⏹️ Stopped music.")

@bot.tree.command(name="skip", description="Skip current song")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc:
        vc.stop()
    await interaction.response.send_message("⏭️ Skipped!")

bot.run(os.environ["TOKEN"])
