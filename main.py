import discord
from discord.ext import commands
import os
import random
import protected

def import_all_songs():
    songs = {
        'battle' : [],
        'boss' : [],
        'idle' : [],
        'victory' : []
    }

    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.mp3') or file.endswith('.ogg'):
                if 'battle' in root:
                    songs['battle'].append(os.path.join(root, file))
                elif 'boss1' in root:
                    songs['boss1'].append(os.path.join(root, file))
                elif 'idle' in root:
                    songs['idle'].append(os.path.join(root, file))
                elif 'victory' in root:
                    songs['victory'].append(os.path.join(root, file))

    return songs

def main():
    songs = import_all_songs()

    credentials = protected.Protected()

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    loop_state = {}
    volume_state = {}

    def after_play(ctx, song):
        if loop_state.get(ctx.guild.id, False):
            ctx.voice_client.play(discord.FFmpegPCMAudio(song), after=lambda e: after_play(ctx, song))

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

    @bot.command()
    async def leave(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Left the voice channel.')
        else:
            await ctx.send('I am not connected to a voice channel.')

    @bot.command()
    async def play_battle(ctx):
        loop_state[ctx.guild.id] = True
        volume_state[ctx.guild.id] = 0.1
        if songs['battle']:
            rand_song = random.choice(songs['battle'])
            if ctx.voice_client:
                song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(rand_song), volume=volume_state[ctx.guild.id])
                ctx.voice_client.play(song, after=lambda e: after_play(ctx, song))
                await ctx.send(f'Playing {rand_song}')
        else:
            await ctx.send('No battle songs found.')

    @bot.command()
    async def play_boss(ctx):
        loop_state[ctx.guild.id] = True
        volume_state[ctx.guild.id] = 0.1
        if songs['boss']:
            rand_song = random.choice(songs['boss'])
            if ctx.voice_client:
                song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(rand_song), volume=volume_state[ctx.guild.id])
                ctx.voice_client.play(song, after=lambda e: after_play(ctx, song))
                await ctx.send(f'Playing {rand_song}')
        else:
            await ctx.send('No boss songs found.')

    @bot.command()
    async def play_idle(ctx):
        loop_state[ctx.guild.id] = True
        volume_state [ctx.guild.id] = 0.1
        if songs['idle']:
            rand_song = random.choice(songs['idle'])
            if ctx.voice_client:
                song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(rand_song), volume=volume_state[ctx.guild.id])
                ctx.voice_client.play(song, after=lambda e: after_play(ctx, song))
                await ctx.send(f'Playing {rand_song}')
        else:
            await ctx.send('No idle songs found.')

    @bot.command()
    async def play_victory(ctx):
        loop_state[ctx.guild.id] = True
        volume_state [ctx.guild.id] = 0.1
        if songs['victory']:
            rand_song = random.choice(songs['victory'])
            if ctx.voice_client:
                song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(rand_song), volume=volume_state[ctx.guild.id])
                ctx.voice_client.play(song, after=lambda e: after_play(ctx, song))
                await ctx.send(f'Playing {rand_song}')
        else:
            await ctx.send('No victory songs found.')

    @bot.command()
    async def stop(ctx):
        if ctx.voice_client:
            loop_state[ctx.guild.id] = False
            ctx.voice_client.stop()
            await ctx.send('Stopped playing.')
        else:
            await ctx.send('I am not connected to a voice channel.')

    bot.run(credentials.get_token())

if __name__ == '__main__':
    main()