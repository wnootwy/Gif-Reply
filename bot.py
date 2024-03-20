import os, random, requests, json, discord, nltk, pytesseract, io
from dotenv import load_dotenv
from discord.ext import commands
from PIL import Image


pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Parker\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'



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
        print(message.content)
        userMessage = message.content[23:].split("-")

        # Remove ID from end of userMessage list.
        userMessage.remove(userMessage[-1])


        # Define keywords into a list that don't include stop words
        keywords = []

        # Iterate over elements and index of a list
        for i, word in enumerate(userMessage):

            # If the word isn't a stop word, add it to the keywords list in lowercase to be tested for it's tag
            if word.lower() not in STOPWORDS:
                keywords.append(userMessage[i].lower())

        # Add tags to the keywords (Noun, Verb, Adverb)
        tagKeywords = nltk.pos_tag(keywords)

        # Create a list for each tag to create search key later
        nouns = [word for word, tag in tagKeywords if tag.startswith('N') and word not in STOPWORDS]
        verbs = [word for word, tag in tagKeywords if tag.startswith('VB')]
        adverbs = [word for word, tag in tagKeywords if tag.startswith('RB')]
        adjectives = [word for word, tag in tagKeywords if tag.startswith('JJ')]

        # Now that nouns have been defined we reset keywords to help find the subject of the GIF
        keywords = []
        for word in range(len(nouns)):

            # Capitalize each word in nouns so NLTK can do a proper Name Entity Recognition
            nouns[word] = nouns[word].capitalize()
            
        # Retag as we did earlier    
        keywords = nltk.pos_tag(nouns)

        # Chunk the keywords to determine if person
        nounEntities = nltk.chunk.ne_chunk(keywords)
        # Iterate through the entities determined by NLTK
        for entity in nounEntities:

            # Entity is marked as PERSON
            if isinstance(entity, nltk.tree.Tree) and entity.label() == 'PERSON':
                
                # Store person_name here and break as we only need the first name, mostly likely the subject
                person_name = ' '.join([word for word, tag in entity.leaves()])
                break
            elif not nouns and not verbs and not adverbs and not adjectives:
                imageToText(message.content)
            else:
                person_name = random.choice(nouns)
        try:
            person_name
            keyword = "{} {} {} {}".format(random.choice(adjectives) if adjectives else "", 
                                                person_name if person_name else random.choice(nouns), 
                                                random.choice(verbs) if verbs else "", 
                                                random.choice(adverbs) if adverbs else "")
        except UnboundLocalError:
            keyword = " ".join(imageToText(message.content))
        print("Keyword:", keyword)

        print(f"Nouns:{nouns},\n Verbs:{verbs},\nAdverbs:{adverbs}, \nAdjectives:{adjectives}")
        #print(f"PersonName{person_name}")
        
            

        TENOR_TOKEN = os.getenv('TENOR_TOKEN')
        print(keyword)

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


# Pass the media.tenor.com link, and the nouns list or create a new nouns list

def imageToText(link):
    img = requests.get(f'{link}'+".gif", stream=True).content
    img = Image.open(io.BytesIO(img))
    text = pytesseract.image_to_string(img)
    for frame in range(1):

        img.seek(frame)

        imgrgb = img.convert('RGBA')

        imgrgb.show()

        text = pytesseract.image_to_string(imgrgb, config='--psm 6')

        text = text.split()
        
        return text

bot.run(TOKEN)


"""
1) Add feature to store tier lists in a db maybe? utilize a command to save it?
2) Random gng memes command



"""