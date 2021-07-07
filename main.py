import os
import discord

#brings in the hidden token
Discord_Token = os.environ['TOKEN']

client = discord.Client()

#When bot is ready, it will say it is logged in
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

#Event triggers each time a message is received
@client.event
async def on_message(message):
  #If the creator of the message is the bot it will not 'scan' it
  if message.author == client.user:
    return
  
  #If the user says hello with the '=' prefix 
  if message.content.startswith('=Hello'):
    await message.channel.send('Hello')

#Runs Discord Bot
client.run(Discord_Token)

 

