import os
import time
import unidecode

#discord/server
import discord
from keep_alive import keep_alive

#scraping
import requests
from bs4 import BeautifulSoup

#database
from replit import db

#brings in the hidden token
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
RAPID_API_KEY = os.environ['RAPID_API_KEY']

client = discord.Client()


def scrape_image(player_id, full_name):
	try:
		#scraping for current nba player
		player_link = f'https://www.nba.com/player/{player_id}'
		header = {"From": "Daniel Agapov <danielagapov1@gmail.com>"}

		response = requests.get(player_link, headers=header)
		if response.status_code != 200: print("Failed to get HTML:", response.status_code, response.reason); exit()

		current_soup = BeautifulSoup(response.text, "html5lib")

		image_address = current_soup.select(r'div > div.block.w-1\/2.md\:w-1\/3 > img')[0]['src']
		return str(image_address)
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

		image_address = historic_soup.select(r'#meta > div.media-item > img')[0]['src']

		return str(image_address)

#When bot is ready, it will say it is logged in
@client.event
async def on_ready():
	print(f"We have logged in as {client.user}")
	
	#change if doing maintenance, etc.
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='to =help'))

#Event triggers each time a message is received

@client.event
async def on_message(message):
	global message_channel
	message_channel = message.channel
	#removes accents since API does not accept them
	message.content=unidecode.unidecode(message.content)

	#bulletproofing input
	text=message.content.upper()

	#If the creator of the message is the bot it will not 'scan' it
	if message.author == client.user:
		return

	#If the user says commands with the '=' prefix 
	if text == '=HELP':
		async with message.channel.typing():

			help_embed=discord.Embed(title="Command List",description="List of Commands for Basketball Bot", color=0xCF352)

			help_embed.add_field(name="=hello",value="Greet the bot",inline=False)

			help_embed.add_field(name="=player",value="Retreive player statistics from the bot by using the '=player' followed by the full name of the player with proper capitalization, ex: =player deMar deRozan for in-word capital letters.",inline=False)

			help_embed.add_field(name="=gn or =good night followed by anything else such as gn! or gn <3",value="Have the bot say goodbye to you in canadian slang",inline=False)

			help_embed.add_field(name="=ping",value="Check the latency of the bot's response to your requests",inline=False)

		await message.channel.send(embed=help_embed)

	#find info on custom players
	if message.content.startswith('=customplayer'):
		async with message.channel.typing():
			split_custom_player_name = message.content.split()[1:]
			custom_player_name, j = '', 0
			for i in split_custom_player_name:
				custom_player_name += str(split_custom_player_name[j]) + ' '
				j += 1
			custom_player_name.replace(custom_player_name[-1], '')
	#add stats to custom players by playing custom game
	if message.content.startswith('=playcustom'):
		async with message.channel.typing():
			pass

	#If the user uses the player command with the '=' prefix
	if message.content.upper().startswith('=PLAYER'):

		async with message.channel.typing():
			name_message = message.content

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

			time.sleep (1)
				
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

				time.sleep(1)

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

				await message.channel.send(embed=list_names_embed)

				if cap_reached==True:
					await message.channel.send(embed=list_names_embed_2)
				
			else:
				#takes player id from response text
				player_id=(str((response.text.split(",")[0]))[8:])
				print(player_id)
				time.sleep(1)

				if player_id == "":
					await message.channel.send(f"There is not enough information available on {full_name}.")

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

					await message.channel.send(embed=player_embed)
	#If the user says hello with the '=' prefix 
	if text == '=HELLO':
		async with message.channel.typing():
			await message.channel.send('Heyyyyyy')
		
	
	if text == '=PING':
		async with message.channel.typing():
			await message.channel.send(f"Ping: {round(client.latency*100)} ms")

	if text.startswith('=GOOD NIGHT') or text.startswith('=GN'):
		async with message.channel.typing():
			await message.channel.send('one time crodie')

#pings website server over and over through the method ran in keep_alive.py with Flask
keep_alive()

#Runs Discord Bot
client.run(DISCORD_TOKEN)	