import discord
from discord.ext import commands
import youtube_dl

# SEEK https://stackoverflow.com/questions/62354887/is-it-possible-to-seek-through-streamed-youtube-audio-with-discord-py-play-from


class music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
		self.YDL_OPTIONS = {'format': "bestaudio"}

		self.is_playing = False
		self.is_paused = False
		self.vc = None
		self.song_queue = []

	def search_yt(self, query):
		with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
			try:
				get_info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
			except Exception:
				return False
		return {'source': get_info['formats'][0]['url'], 'title': get_info['title'], 'duration': get_info['duration'], 'thumbnail': get_info['thumbnail'], 'webpage_url': get_info['webpage_url']}

	def play_next(self):
		if len(self.song_queue) > 0:
			self.is_playing = True
			current = self.song_queue[0][0]['source']
			self.song_queue.pop(0)
			self.vc.play(discord.FFmpegPCMAudio(current, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
		else:
			self.is_playing = False

	async def play_song(self, ctx):
		if len(self.song_queue) > 0:
			self.is_playing = True
			current = self.song_queue[0][0]['source']

			# Connect the the requested voice channel
			if self.vc == None or not self.vc.is_connected():
				self.vc = await self.song_queue[0][1].connect()
				if self.vc == None: # ? Failed to connect 
					await ctx.send("Error: Couldn't connect to the voice channel.")
					return
			else:
				await self.vc.move_to(self.song_queue[0][1])

			await ctx.send(f"🎵 Playing : {self.song_queue[0][0]['title']}")
			self.song_queue.pop(0)
			self.vc.play(discord.FFmpegPCMAudio(current, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
		else:
			self.is_playing = False

	@commands.command(aliases = ['p', 'pl', 'pla', 'plya', 'lypa'])	
	async def play(self, ctx, *args):
		query = " ".join(args)
		print(f"Asked for {query}")

		vc = ctx.author.voice.channel

		if vc is None:
			await ctx.send("You NEED to be in channel.")
		elif self.is_paused:
			self.vc.resume()
		else:
			song = self.search_yt(query)
			if type(song) == type(True):
				await ctx.send("Error: Couldn't find the song.")
			else:
				try:
					if self.is_playing:
						try:
							embed = discord.Embed(	title="Request Added to the Queue", 
													description=f"{song['title']}", 
													color=discord.Color.purple())
							embed.add_field(name="Requested by", value=f"{ctx.author.mention}", inline=True)
							embed.add_field(name="Duration", value=f"{song['duration']} seconds")
							embed.set_thumbnail(url=song['thumbnail'])
							await ctx.send(embed=embed)
						except Exception as e:
							print(e)
				except Exception as e:
					print(e)

				self.song_queue.append([song, vc])

				if self.is_playing == False:
					await self.play_song(ctx)

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

	@commands.command(aliases=['pa'])
	async def pause(self, ctx):
		if self.is_playing:
			self.vc.pause()
			self.is_paused = True
			await ctx.send("⏸️ Paused")
		elif self.is_paused:
			self.vc.resume()
			self.is_paused = False
			await ctx.send("▶️ Resumed")
		else:
			await ctx.send("🔇 Nothing is playing.")

	@commands.command(aliases=['r'])
	async def resume(self, ctx):
		if self.is_paused:
			self.vc.resume()
			self.is_paused = False
			await ctx.send("▶️ Resumed")
		else:
			await ctx.send("🎧 Music is already playing.")

	@commands.command(aliases=['s'])
	async def stop(self, ctx):
		await ctx.voice_client.stop()
		await ctx.send("Music stopped.")

	@commands.command(aliases=['next', 'spik', 'skip', 'fs', 'forceskip',])
	async def skipp(self, ctx):
		if self.vc != None and self.vc:
			self.vc.stop()
			await ctx.send("⏩ Skipped")

	#@commands.command(aliases=['np', 'current', 'currentsong', 'playing'])
	#async def info(self, ctx):
	#	try:
	#		embed = discord.Embed(title="Now playing", description=f"{ctx.voice_client.source.title}", color=ctx.author.color)
	#		embed.add_field(name="Requested by", value=ctx.author.mention)
	#		embed.add_field(name="Duration", value=f"{ctx.voice_client.source.duration} seconds")
	#		embed.set_thumbnail(url=ctx.author.avatar_url)
	#		await ctx.send(embed=embed)
	#	except Exception as e:
	#		print(e)
	#		await ctx.send(f"Error while trying to get the current song. {e}")

async def setup(bot):
	await bot.add_cog(music(bot))