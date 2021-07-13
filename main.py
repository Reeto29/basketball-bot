import os
import discord
import time
import unidecode
from keep_alive import keep_alive

#for scraping
import requests
from bs4 import BeautifulSoup

#brings in the hidden token
Discord_Token = os.environ['TOKEN']
Rapid_API_Key = os.environ['rapidapi_key']


client = discord.Client()

def scrape_image(player_id):
  link_to_player = f'https://www.nba.com/player/{player_id}'
  header = {"From": "Daniel Agapov <danielagapov1@gmail.com>"}

  response = requests.get(link_to_player, headers=header)
  if response.status_code != 200: print("Failed to get HTML:", response.status_code, response.reason); exit()

  soup = BeautifulSoup(response.text, "html5lib")

  
#__next > div.Layout_withNav__2ED2- > div.flex.flex-col.bg-teams-LAL > section.relative.overflow-hidden > div.relative.block.bg-transparent.max-w-screen-xxl.mx-auto > div > div.block.w-1\/2.md\:w-1\/3 > img
  try:
    image_address = soup.select(r'div > div.block.w-1\/2.md\:w-1\/3 > img')[0]['src']
  except: 
    current_player = False

#body > main > div > div > div > div:nth-child(2) > div.stats-player-summary.team-color.TOR > div.stats-teamplayer-summary-container.with-padding > div.stats-player-summary__container > div > div.summary-player__logo > img
  #try:
    # image_address = soup.find_all('img')
    # print(image_address)

  # except: 
  #   current_player = True
  
  #print("current") if current_player else print("historic")



  return str(image_address)

#When bot is ready, it will say it is logged in
@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")

#Event triggers each time a message is received
@client.event
async def on_message(message):

  #removes accents since API does not accept them
  message.content=unidecode.unidecode(message.content)

  #bulletproofing input
  text=message.content.upper()

  #If the creator of the message is the bot it will not 'scan' it
  if message.author == client.user:
    return

  #If the user says commands with the '=' prefix 
  if text == ('=HELP'):

    help_embed=discord.Embed(title="Command List",description="List of Commands for Basketball Bot", color=0xCF352)

    help_embed.add_field(name="=hello",value="Greet the bot",inline=False)
    help_embed.add_field(name="=player",value="Retreive player statistics from the bot by using the '=player'followed by the full name of the player with proper capitalization. ex: =player DeMar DeRozan",inline=False)

    await message.channel.send(embed=help_embed)


  #If the user says hello with the '=' prefix 
  if text == ('=HELLO'):
    await message.channel.send('Hello')

  #If the user uses the player command with the '=' prefix
  if message.content.startswith('=player'):
    full_name = message.content
    full_name=full_name.split(" ")
    full_name=(f"{full_name[1]} {full_name[2]}")
    print (full_name)

    url = "https://nba-stats4.p.rapidapi.com/players/"
    
    querystring = {"full_name":full_name}

    headers = {
        'x-rapidapi-key': str(Rapid_API_Key),
        'x-rapidapi-host': "nba-stats4.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    #print(response.text)

    #takes player id from response text
    player_id=(str((response.text.split(",")[0]))[8:])
    #################################
    time.sleep(1)
    ################################

    if player_id == "":
      await message.channel.send(f"There is not enough information available on {full_name}")

    else:
      
      
      url = f"https://nba-stats4.p.rapidapi.com/per_game_career_regular_season/{player_id}"

      headers = {
        'x-rapidapi-key': str(Rapid_API_Key),
        'x-rapidapi-host': "nba-stats4.p.rapidapi.com"
      }

      response = requests.request("GET", url, headers=headers)


      stat_block=(response.text.split(","))    

      player_stats=[]

      player_embed=discord.Embed(title=f"{full_name} Career Stats",description="Overview on player statistics", color=0xA4D6D1)

      player_embed.set_thumbnail(url=scrape_image(player_id))

      player_stats.append(stat_block[3][7:])  #Games Played
      player_stats.append(stat_block[22][17:-2]) #Point Avg
      player_stats.append(stat_block[17][16:]) #Rebounds
      player_stats.append(stat_block[18][17:]) #Assists
      player_stats.append(stat_block[19][17:]) #Steals
      player_stats.append(stat_block[20][17:]) #Blocks


      player_embed.add_field(name="Games Played",value=f"{player_stats[0]}",inline=False)
      player_embed.add_field(name="Average Points",value=f"{player_stats[1]}",inline=False)
      player_embed.add_field(name="Rebounds",value=f"{player_stats[2]}",inline=False)
      player_embed.add_field(name="Assists",value=f"{player_stats[3]}",inline=False)
      player_embed.add_field(name="Steals",value=f"{player_stats[4]}",inline=False)
      player_embed.add_field(name="Blocks",value=f"{player_stats[5]}",inline=False)
      player_embed.set_footer(text="Basketball Bot")

      await message.channel.send(embed=player_embed)


#pings website server over and over through the method ran in keep_alive.py with Flask
keep_alive()

#Runs Discord Bot
client.run(Discord_Token)