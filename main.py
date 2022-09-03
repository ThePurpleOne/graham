from discord.ext import commands,tasks
from dotenv import load_dotenv
import youtube_dl
import music_cog
import asyncio
import discord
import os


async def load_extensions():
	await bot.load_extension(f"music_cog")

async def main():

	async with bot:
		await load_extensions()
		await bot.start(token)


if __name__ == "__main__":

	# LOAD ENVIRONMENT VARIABLES
	load_dotenv()
	token = os.getenv("TOKEN")
	owner = os.getenv("OWNER")
	prefix = os.getenv("PREFIX")

	# CREATE THE ACTUAL BOT
	bot = commands.Bot(command_prefix=prefix, owner_id=owner, intents=discord.Intents.all())

	# RUN THE BOT
	asyncio.run(main())