import os, random, requests, json, discord, nltk
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(intents=discord.Intents.all(),command_prefix='!')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@bot.event#command(name='annoy', help="A command that will reply to every tenor GIF sent by any user in the server.")
async def on_message(message):

    # Avoid bot recursion
    if message.author == bot.user:
        return
    
    # User has sent a gif
    elif "https://tenor.com/view" in message.content:

        # Ignore these words
        STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into", "is", "it", "no", 
    "not", "of", "on", "or", "such", "that", "the", "their", "then", "there", "these", "they", "this", "to", 
    "was", "will", "with", "gif", "image", "do", 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
    'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
    "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't",
    'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
    'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", "im"
}

        
        # Extract last half of URL and transform into list to be used {as keywords
        userMessage = message.content[23:].split("-")
        userMessage.remove(userMessage[-1])
        print(f"Gif Title:{userMessage}")
        keywords = []
        for i, word in enumerate(userMessage):
            userMessage[i] = word.capitalize()
            if word.lower() not in STOPWORDS:
                keywords.append(userMessage[i].lower())

        tagKeywords = nltk.pos_tag(keywords)

        nouns = [word for word, tag in tagKeywords if tag.startswith('N') and word not in STOPWORDS]
        verbs = [word for word, tag in tagKeywords if tag.startswith('VB')]
        adverbs = [word for word, tag in tagKeywords if tag.startswith('RB')]
        adjectives = [word for word, tag in tagKeywords if tag.startswith('JJ')]


        keywords = []
        for word in range(len(nouns)):
            nouns[word] = nouns[word].capitalize()
            
            
        keywords = nltk.pos_tag(nouns)
        nounEntities = nltk.chunk.ne_chunk(keywords)
        for entity in nounEntities:
            if isinstance(entity, nltk.tree.Tree) and entity.label() == 'PERSON':

                person_name = ' '.join([word for word, tag in entity.leaves()])
                break
        print("Person: %s" % person_name)

        keyword = "{}-{}-{}-{}".format(random.choice(adjectives) if adjectives else "", 
                                    person_name if person_name else round.choice(nouns), random.choice(verbs) if verbs else "", random.choice(adverbs) if adverbs else "")
        print(keyword)
        # Choose a word until a stop word has not been chosen
        """while True:
            keyword = random.choice(keywords)
            if keyword not in STOPWORDS:
                break
"""
        # Leave here to study how well a keyword performs
        print("keywordsssss %s" % keyword)

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


bot.run(TOKEN)