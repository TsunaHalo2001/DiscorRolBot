import discord
from discord.ext import commands
import os
import random
import protected

IDLE_LOCATIONS = ('tavern', 'field', 'city', 'dungeon')
PLAY_CATEGORIES = ('battle', 'boss', 'dragon', 'skeleton', 'victory', 'heal')

def import_all_songs():
    songs = {
        'battle': [],
        'boss': [],
        'idle': {
            'tavern': [],
            'field': [],
            'city': [],
            'dungeon': []
        },
        'victory': [],
        'heal': [],
        'dragon': [],
        'skeleton': [],
    }

    for root, _, files in os.walk('src'):
        for file in files:
            if not (file.endswith('.mp3') or file.endswith('.ogg')):
                continue

            song_path = os.path.join(root, file)
            if 'idle' in root:
                for location in IDLE_LOCATIONS:
                    if location in root:
                        songs['idle'][location].append(song_path)
                        break
                continue

            for category in PLAY_CATEGORIES:
                if category in root:
                    songs[category].append(song_path)
                    break

    return songs

def main():
    songs = import_all_songs()

    credentials = protected.Protected()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    loop_state = {}
    volume_state = {}

    def get_voice_client(ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return None
        return voice_client

    def get_song_pool(category, location=None):
        if category == 'idle':
            if location:
                return songs['idle'].get(location, [])
            all_idle_songs = []
            for idle_location in IDLE_LOCATIONS:
                all_idle_songs.extend(songs['idle'].get(idle_location, []))
            return all_idle_songs
        if category in PLAY_CATEGORIES:
            return songs[category]
        return []

    def after_play(ctx, song):
        voice_client = get_voice_client(ctx)
        if not voice_client:
            return

        if loop_state.get(ctx.guild.id, False):
            voice_client.play(
                discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song),
                    volume=volume_state[ctx.guild.id]
                ),
                after=lambda e: after_play(ctx, song)
            )

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')

    @bot.command()
    async def ping(ctx):
        await ctx.send('Pong!')

    @bot.command()
    async def join(ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f'Joined {channel}')
        else:
            await ctx.send('You are not connected to a voice channel.')

    async def stop_song(ctx):
        voice_client = get_voice_client(ctx)
        if not voice_client:
            await ctx.send('I am not connected to a voice channel.')
            return

        loop_state[ctx.guild.id] = False
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

    @bot.command()
    async def leave(ctx):
        voice_client = get_voice_client(ctx)
        if not voice_client:
            await ctx.send('I am not connected to a voice channel.')
            return

        await stop_song(ctx)
        await voice_client.disconnect()
        await ctx.send('Left the voice channel.')

    async def play_song(ctx, category, location=None):
        voice_client = get_voice_client(ctx)
        if not voice_client:
            await ctx.send('I am not connected to a voice channel.')
            return

        loop_state[ctx.guild.id] = True
        volume_state[ctx.guild.id] = 0.1

        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

        category_songs = get_song_pool(category, location)

        if not category_songs:
            await ctx.send(f'No {category} songs found.')
            return

        rand_song = random.choice(category_songs)
        song = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(rand_song),
            volume=volume_state[ctx.guild.id]
        )

        if category == 'heal':
            loop_state[ctx.guild.id] = False

        voice_client.play(song, after=lambda e: after_play(ctx, rand_song))
        await ctx.send(f'Playing {os.path.basename(rand_song)}')

    @bot.command()
    async def play(ctx, category: str, location: str = None):
        category = category.lower()

        if category == 'idle':
            if not location:
                await ctx.send('For idle music use: !play idle <tavern|field|city|dungeon>')
                return

            location = location.lower()
            if location not in songs['idle']:
                await ctx.send('Invalid location. Please choose from tavern, field, city, or dungeon.')
                return

            await play_song(ctx, 'idle', location)
            return

        if category not in PLAY_CATEGORIES:
            valid = ', '.join(list(PLAY_CATEGORIES) + ['idle'])
            await ctx.send(f'Invalid category. Choose one of: {valid}.')
            return

        await play_song(ctx, category)

    @bot.command()
    async def play_battle(ctx):
        await play_song(ctx, 'battle')

    @bot.command()
    async def play_boss(ctx):
        await play_song(ctx, 'boss')

    @bot.command()
    async def play_dragon(ctx):
        await play_song(ctx, 'dragon')

    @bot.command()
    async def play_skeleton(ctx):
        await play_song(ctx, 'skeleton')

    @bot.command()
    async def play_idle(ctx, location: str):
        if location in songs['idle']:
            await play_song(ctx, 'idle', location)
        else:
            await ctx.send('Invalid location. Please choose from tavern, field, city, or dungeon.')

    @bot.command()
    async def play_victory(ctx):
        await play_song(ctx, 'victory')

    @bot.command()
    async def play_heal(ctx):
        await play_song(ctx, 'heal')

    @bot.command()
    async def stop(ctx):
        await stop_song(ctx)

    bot.run(credentials.get_token())

if __name__ == '__main__':
    main()