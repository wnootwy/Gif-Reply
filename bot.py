import os, random, requests, json, discord, nltk, pytesseract, io, datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks
from PIL import Image


# Set path for pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Parker\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

sailerTime = datetime.time(hour=10, minute=35, second=0)

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
    if not congratsSailer.is_running():
        congratsSailer.start()
        print("started sailer")

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )
@bot.command(name="neil", description="Sends a meme of Neil")
async def NeilMeme(message):
    meme = ["https://media1.tenor.com/images/5f4b8c797ede65c684d850ccffb90d68/tenor.gif?itemid=18971104"]
    response = random.choice(meme)
    await message.channel.send(response)
    

@tasks.loop(time=sailerTime)
async def congratsSailer():
    channel = bot.get_channel(1215301644242395186)
    await channel.send(file=discord.File(r'C:\Users\Parker\Desktop\Discord Bot\CongratsSailer.mp4'))
    print("is working")


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
            # If all of these lists are empty, then the title is uselss, fetch the image's text
            elif not nouns and not verbs and not adverbs and not adjectives:
                imageToText(message.content)
            # If no person name then choose a random noun for the subject
            else:
                person_name = random.choice(nouns)
        # If person_name is not defined, then we will set the keyword using text from the image with Pytesseract
        try:
            person_name
            keyword = "{} {} {} {}".format(random.choice(adjectives) if adjectives else "", 
                                                person_name if person_name else random.choice(nouns), 
                                                random.choice(verbs) if verbs else "", 
                                                random.choice(adverbs) if adverbs else "")
        except UnboundLocalError:
            keyword = " ".join(imageToText(message.content))          

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
    # Process any commands that may appear in the message
    await bot.process_commands(message) 
    if message.content[0] == "!":
        print(message.content)
        await message.delete()


# Pass the media.tenor.com link, and the nouns list or create a new nouns list

def imageToText(link):

    # Get the url from the message and add .gif to redirect to a page just containing a gif that we can work with
    img = requests.get(f'{link}'+".gif", stream=True).content

    # Open the image file as a bytes stream
    img = Image.open(io.BytesIO(img))

    # Use a for loop to turn the first frame into an image so pytesseract can read the text
    for frame in range(1):

        img.seek(frame)

        imgrgb = img.convert('RGBA')

        #imgrgb.show() # Add this in for debugging the image being pulled

        # Convert image text to string. NOTE: # PSM 6 assumes a single uniform block of text which seems to yield the best results
        text = pytesseract.image_to_string(imgrgb, config='--psm 6')

        # Break the text into a list
        text = text.split()
        
        # Return text to be used as the keyword later
        return text

bot.run(TOKEN)


"""
1) Add feature to store tier lists in a db maybe? utilize a command to save it?
2) Random gng memes command



"""