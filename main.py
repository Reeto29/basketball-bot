import os
import time
import unidecode
from random import randint

#discord/server
import discord
from discord.ext import commands
from keep_alive import keep_alive
from discord_buttons_plugin import *

#scraping
import requests
from bs4 import BeautifulSoup

#brings in the hidden token
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
RAPID_API_KEY = os.environ['RAPID_API_KEY']

#setting prefix and initializing bot and setting case sensitivity for commands
client = commands.Bot(command_prefix=('= ', '='), case_insensitive = True )

client.remove_command("help")

buttons=ButtonsClient(client)
######################

example_embed=discord.Embed(title="Example Embed Page 1",description="Example Embed", color=0xCF352)

example_embed.add_field(name="Test",value="test to see if the buttons go on embeds this wat",inline=False)

example_embed_2=discord.Embed(title="Example Embed Page 2",description="Example Embed", color=0xCF352)

example_embed_2.add_field(name="Test",value="test to see if the buttons go on embeds this wat",inline=False)

@client.command()
async def create(ctx):
	await buttons.send(
		content = "This is an example message!", 
		embed=example_embed,
		channel = ctx.channel.id,
		components = [
			ActionRow([
				Button(
					label="<", 
					style=ButtonType().Primary, 
					custom_id="button_one"
				),Button(
					label=">",
					style=ButtonType().Primary,
					custom_id="button_two"
				)
			])
		]
	)

@buttons.click
async def button_one(ctx):
	await ctx.reply(embed=example_embed)

@buttons.click
async def button_two(ctx):
	await ctx.reply(embed=example_embed_2)
	

##############

def scrape_image(player_id, full_name):
	try:
		#scraping for current nba player
		player_link = f'https://www.nba.com/player/{player_id}'
		header = {"From": "Daniel Agapov <danielagapov1@gmail.com>"}

		response = requests.get(player_link, headers=header)
		if response.status_code != 200: print("Failed to get HTML:", response.status_code, response.reason); exit()

		current_soup = BeautifulSoup(response.text, "html5lib")

		return str(current_soup.select(r'div > div.block.w-1\/2.md\:w-1\/3 > img')[0]['src'])
	except: 
		#must be historic, so tries this exception

		#(first 5 letters of last name) + (first 2 letters of first name)
		last_name, first_name = full_name.split()[-1].lower(), full_name.split()[0].lower()
		
		name_for_link = last_name[:5] if len(last_name) > 4 else last_name[:len(last_name)] 

		name_for_link += first_name[:2] if len(first_name) > 1 else first_name[:len(first_name)]

		player_link = f'https://www.basketball-reference.com/players/{last_name[0]}/{name_for_link}01.html'

		header = {"From": "Daniel Agapov <danielagapov1@gmail.com>"}

		response = requests.get(player_link, headers=header)

		if response.status_code != 200: print("Failed to get HTML:", response.status_code, response.reason); exit()
		
		historic_soup = BeautifulSoup(response.text, "html5lib")

		return str(historic_soup.select(r'#meta > div.media-item > img')[0]['src'])

def randomize_sleep(min, max):
    time.sleep(randint(min*100, max*100) / 100)

#When bot is ready, it will say it is logged in
@client.event
async def on_ready():
	print(f"We have logged in as {client.user}")
	
	#change if doing maintenance, etc.
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='to =help'))

@client.command()
async def help(ctx):
	#async with ctx.typing():

	help_embed=discord.Embed(title="Command List",description="List of Commands for Basketball Bot", color=0xCF352)

	help_embed.add_field(name="=hello",value="Greet the bot",inline=False)

	help_embed.add_field(name="=player",value="Retreive player statistics from the bot by using the '=player' followed by the full name of the player with proper capitalization, ex: =player deMar deRozan for in-word capital letters.",inline=False)

	help_embed.add_field(name="=gn or =good night followed by anything else such as gn! or gn <3",value="Have the bot say goodbye to you in canadian slang",inline=False)

	help_embed.add_field(name="=ping",value="Check the latency of the bot's response to your requests",inline=False)

	await ctx.send(embed=help_embed)


@client.command()
async def player(ctx):
	async with ctx.typing():
		name_message = unidecode.unidecode(ctx.message.content)

		name_message_words=name_message.split(" ")

		full_name = [name_message_words[0]]
		for word in name_message_words[1:]:
			full_name.append(word[0].upper() + word[1:])

		#formatting player names
		if len(full_name) < 3:
			querystring = {"first_name":full_name[1]}
		
		if len(full_name) == 3:
			full_name=(f"{full_name[1]} {full_name[2]}")
			querystring = {"full_name":full_name}

		randomize_sleep(1, 2)
			
		url = "https://nba-stats4.p.rapidapi.com/players/"

		headers = {
			'x-rapidapi-key': str(RAPID_API_KEY),
			'x-rapidapi-host': "nba-stats4.p.rapidapi.com"
			}
		response = requests.request("GET", url, headers=headers, params=querystring)

		if len(full_name) < 3:
			cap_reached=False

			first_name_query=response.text
			first_name_query=first_name_query.replace(":",",")
			first_name_query=first_name_query.split(",")

			randomize_sleep(1, 2)

			querystring = {"last_name":full_name[1]}

			url = "https://nba-stats4.p.rapidapi.com/players/"

			headers = {
				'x-rapidapi-key': str(RAPID_API_KEY),
				'x-rapidapi-host': "nba-stats4.p.rapidapi.com"
				}
			response = requests.request("GET", url, headers=headers, params=querystring)

			last_name_query=response.text
			last_name_query=last_name_query.replace(":",",")
			last_name_query=last_name_query.split(",")

			name_query=first_name_query + last_name_query

			list_names_embed=discord.Embed(title=f"Full Name List",description="Please choose one of these players from the list", color=0xA4D6D1)

			list_names_embed_2=discord.Embed(title=f"Full Name List 2",description="Please choose one of these players from the list", color=0xA4D6D1)


			list_names=[]
			try:
				for i in range(len(name_query)):
					full_name_position=name_query.index(' "full_name"')
					name_query.pop(full_name_position)

					list_names.append(name_query[full_name_position][2:-1])
			except:
				pass
			for i in range(len(list_names)):
				list_names_embed.add_field(name=f"Player {i+1}",value=f"{list_names[i]}",inline=True)
				if i > 24:
					cap_reached=True
					list_names_embed_2.add_field(name=f"Player {i+1}",value=f"{list_names[i]}",inline=True)

			if len(list_names) != 0:
				await ctx.send(embed=list_names_embed)
			else:
				await ctx.send(f"There is not enough information available on {full_name[-1]}.")

			if cap_reached==True:
				await ctx.send(embed=list_names_embed_2)
			
		else:
			#takes player id from response text
			player_id=(str((response.text.split(",")[0]))[8:])
			randomize_sleep(1, 2)

			if player_id == "":
				await ctx.send(f"There is not enough information available on {full_name}.")

			else:
				url = f"https://nba-stats4.p.rapidapi.com/per_game_career_regular_season/{player_id}"

				headers = {
				'x-rapidapi-key': str(RAPID_API_KEY),
				'x-rapidapi-host': "nba-stats4.p.rapidapi.com"
				}

				response = requests.request("GET", url, headers=headers)

				stat_block=(response.text.split(",")) 

				player_stats=[]

				player_embed=discord.Embed(title=f"{full_name} Career Stats",description="Overview on player statistics", color=0xA4D6D1)

				try:player_embed.set_thumbnail(url=scrape_image(player_id, full_name))
				except:print("Thumbnail image scrape not working")

				try:
					player_stats.append(stat_block[3][7:])	#Games Played
					player_embed.add_field(name="Games Played",value=f"{player_stats[0]}",inline=False)
				except:pass

				try:
					player_stats.append(stat_block[22][17:-2])	#Point Avg
					player_embed.add_field(name="Average Points",value=f"{player_stats[1]}",inline=False)
				except:print("Average Points not working")

				try:
					player_stats.append(stat_block[17][16:]) #Rebounds
					player_embed.add_field(name="Rebounds",value=f"{player_stats[2]}",inline=False)
				except:print("Rebound stats not working")

				try:
					player_stats.append(stat_block[18][17:]) #Assists
					player_embed.add_field(name="Assists",value=f"{player_stats[3]}",inline=False)
				except:print("Assist Stats not working")

				try:
					player_stats.append(stat_block[19][17:]) #Steals
					player_embed.add_field(name="Steals",value=f"{player_stats[4]}",inline=False)
				except:print("Steal stats not working")

				try:
					player_stats.append(stat_block[20][17:]) #Blocks
					player_embed.add_field(name="Blocks",value=f"{player_stats[5]}",inline=False)
				except:print("Block stats not working")

				player_embed.set_footer(text="Basketball Bot")

				await ctx.send(embed=player_embed)


@client.command()
async def hello(ctx):
	async with ctx.typing():
		await ctx.send('Heyyyyyy')

@client.command(aliases=["goodnight", "gn"])
async def good_night(ctx):
	async with ctx.typing():
		await ctx.send('one time crodie')

@client.command()
async def ping(ctx):
	async with ctx.typing():
		await ctx.send(f"Ping: {round(client.latency*100)} ms")		

#pings website server over and over through the method ran in keep_alive.py with Flask
keep_alive()

#Runs Discord Bot
client.run(DISCORD_TOKEN)	