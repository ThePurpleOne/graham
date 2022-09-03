import discord
from discord.ext import commands
import youtube_dl


class music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
		self.YDL_OPTIONS = {'format': "bestaudio"}

	def search_yt(self, query):
		with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
			try:
				get_info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
			except Exception:
				return False
		return {'source': get_info['formats'][0]['url'], 'title': get_info['title']}

	@commands.command(aliases=['j',])
	async def join(self, ctx):
		if ctx.author.voice is None: 
			await ctx.send("Go in the channel to play something.")
		if ctx.voice_client is None: 
			await ctx.author.voice.channel.connect()
			
	@commands.command(aliases=['fuckoff','gtfo', 'leave', 'quit'])
	async def disconnect(self, ctx):
		try:
			await ctx.voice_client.disconnect()
		except Exception as e:
				print(e)
				await ctx.send(f"Error while trying to disconnect. {e}")

	@commands.command()
	async def play(self, ctx, *args):
		query = " ".join(args)
		print(f"Asked for {query}")

		if ctx.author.voice is None: 
			await ctx.send("Go in the channel to play something.")
		if ctx.voice_client is None: 
			await ctx.author.voice.channel.connect()

		ctx.voice_client.stop()
		url = self.search_yt(query)

		if type(url) == type(True):
			await ctx.send("No song found.")
		else:
			try:
				source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url['source'], **self.FFMPEG_OPTIONS))
				ctx.voice_client.play(source)
				await ctx.send(f"🎵 Playing : {url['title']}")
			except Exception as e:
				print(e)
				await ctx.send(f"Error while trying to play the song. {e}")

	@commands.command()
	async def pause(self, ctx):
		await ctx.voice_client.pause()
		await ctx.send("Music paused. Use `resume` to resume.")

	@commands.command()
	async def resume(self, ctx):
		await ctx.voice_client.resume()
		await ctx.send("Music resumed.")

async def setup(bot):
	await bot.add_cog(music(bot)) 