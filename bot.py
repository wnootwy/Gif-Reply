import os, random, discord, requests, json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')
@client.event
async def on_message(message):

    # Avoid bot recursion
    if message.author == client.user:
        return
    
    # User has sent a gif
    elif "https://tenor.com/view" in message.content:

        # Ignore these words
        stopWords = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it", "no", 
                     "not", "of", "on", "or", "such", "that", "the", "their", "then", "there", "these", "they", "this", "to", 
                     "was", "will", "with", "gif", "image", "do"]
        
        # Extract last half of URL and transform into list to be used as keywords
        keywords = message.content[23:].split("-")
        keywords.remove(keywords[-1])
        
        # Choose a word until a stop word has not been chosen
        while True:
            keyword = random.choice(keywords)
            if keyword not in stopWords:
                break

        # Leave here to study how well a keyword performs
        print(keyword)


        TENOR_TOKEN = os.getenv('TENOR_TOKEN')

        # Query tenor API to select a gif
        r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&limit=1" % (keyword, TENOR_TOKEN))
        if r.status_code == 200:
            response = json.loads(r.content)

            # Index response content to obtain the proper tenor link
            response = response['results'][0]['itemurl']

            # Send the GIF after a user has sent the message
            await message.channel.send(response)
        else:

            # No result
            response = None


client.run(TOKEN)