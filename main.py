import os
import discord
import requests
import time


#brings in the hidden token
Discord_Token = os.environ['TOKEN']

client = discord.Client()


#When bot is ready, it will say it is logged in
@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")

#Event triggers each time a message is received
@client.event
async def on_message(message):
  #If the creator of the message is the bot it will not 'scan' it

  text=message.content.upper()

  if message.author == client.user:
    return

  #If the user says commands with the '=' prefix 
  if text == ('=COMMAND'):
    await message.channel.send("""Command List:
    1. =Hello""")

  #If the user says hello with the '=' prefix 
  if text == ('=HELLO'):
    await message.channel.send('Hello')

  if message.content.startswith('=player'):
    full_name = message.content
    full_name=full_name.split(" ")
    full_name=(f"{full_name[1]} {full_name[2]}")
    print (full_name)

    url = "https://nba-stats4.p.rapidapi.com/players/"
    querystring = {"full_name":{full_name}}
    headers = {
        'x-rapidapi-key': "9cd1a916bcmsh0240719c8d1daa2p120815jsn87d2095a1245",
        'x-rapidapi-host': "nba-stats4.p.rapidapi.com"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    #print(response.text)
    #takes player id from response text
    player_id=(str((response.text.split(",")[0]))[8:])
    #print(player_id)
    #################################
    time.sleep(2)
    ################################

    if player_id == "":
      await message.channel.send(f"There is not enough information available on {full_name}")

    else:
      url = f"https://nba-stats4.p.rapidapi.com/per_game_career_regular_season/{player_id}"
      headers = {
          'x-rapidapi-key': "9cd1a916bcmsh0240719c8d1daa2p120815jsn87d2095a1245",
          'x-rapidapi-host': "nba-stats4.p.rapidapi.com"
          }
      response = requests.request("GET", url, headers=headers)
      stat_block=(response.text.split(","))
      print(stat_block)

      player_stats=[]

      player_stats.append(stat_block[3][7:])  #Games Played
      player_stats.append(stat_block[22][17:-2]) #Point Avg
      player_stats.append(stat_block[17][16:]) #Rebounds
      player_stats.append(stat_block[18][17:]) #Assists
      player_stats.append(stat_block[19][17:]) #Steals
      player_stats.append(stat_block[20][17:]) #Blocks

      await message.channel.send(f"""
      {full_name} Career Stats:
      {player_stats[0]} Games Played
      {player_stats[1]} Point Avg
      {player_stats[2]} Rebounds
      {player_stats[3]} Assists
      {player_stats[4]} Steals
      {player_stats[5]} Blocks
      """)


#####################################################







#Runs Discord Bot
client.run(Discord_Token)

 

