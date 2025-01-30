import os
import logging
import telebot
import google.generativeai as genai
from pymongo import MongoClient
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



# Initialize services
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = MongoClient(
    MONGO_URI, 
    tls=True, 
    tlsAllowInvalidCertificates=True
)
db = client["telegram_bot"]
users_collection = db["users"]
chats_collection = db["chats"]
files_collection = db["files"]

genai.configure(api_key=GEMINI_API_KEY)

def register_user(message):
    chat_id = message.chat.id
    first_name = message.chat.first_name
    username = message.chat.username or "Unknown"
    user = users_collection.find_one({"chat_id": chat_id})
    
    if not user:
        users_collection.insert_one({
            "chat_id": chat_id,
            "first_name": first_name,
            "username": username,
            "phone_number": None
        })
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = KeyboardButton("📱 Share Phone Number", request_contact=True)
        markup.add(button)
        bot.send_message(chat_id, "Please share your phone number to complete registration:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "You are already registered!")

@bot.message_handler(content_types=['contact'])
def save_contact(message):
    chat_id = message.chat.id
    phone_number = message.contact.phone_number
    users_collection.update_one({"chat_id": chat_id}, {"$set": {"phone_number": phone_number}})
    bot.send_message(chat_id, "✅ Registration complete! You can now use the bot.", reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(commands=['start'])
def start(message):
    register_user(message)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_text = message.text

    response = "Sorry, I couldn't process that."
    try:
        # Create a model instance
        model = genai.GenerativeModel("gemini-pro")
        gemini_response = model.generate_content(user_text)
        
        # Extract the response text
        response = gemini_response.text
        
        # Save chat history in MongoDB
        chats_collection.insert_one({
            "chat_id": chat_id,
            "user_input": user_text,
            "bot_response": response,
            "timestamp": message.date
        })
    except Exception as e:
        logging.error(f"Error processing message: {e}")

    bot.send_message(chat_id, response)


# @bot.message_handler(content_types=['photo', 'document'])
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

@bot.message_handler(content_types=['photo', 'document'])
def handle_files(message):
    chat_id = message.chat.id

    # Handle Images
    if message.photo:
        file_id = message.photo[-1].file_id  # Highest resolution
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"

        # Download image
        response = requests.get(file_url)
        image = Image.open(BytesIO(response.content))

        # Generate real analysis
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            gemini_response = model.generate_content([image, "Describe this image in detail."])
            analysis = gemini_response.text
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            analysis = "❌ Failed to analyze the image."

    # Handle Documents
    elif message.document:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"

        # Generate text-based analysis
        try:
            model = genai.GenerativeModel("gemini-pro")
            gemini_response = model.generate_content(f"Analyze the content of this document: {file_url}")
            analysis = gemini_response.text
        except Exception as e:
            logging.error(f"Error processing document: {e}")
            analysis = "❌ Failed to analyze the document."

    # Save metadata to MongoDB
    files_collection.insert_one({
        "chat_id": chat_id,
        "file_id": file_id,
        "file_url": file_url,
        "description": analysis,
        "timestamp": message.date
    })

    # Send the response
    bot.send_message(chat_id, f"📄 Analysis: {analysis}")


@bot.message_handler(commands=['websearch'])
def web_search(message):
    bot.send_message(message.chat.id, "🔍 Enter your search query:")
    bot.register_next_step_handler(message, perform_search)

def perform_search(message):    
    query = message.text
    search_result = "Here are the top results for your query (dummy data)."
    bot.send_message(message.chat.id, search_result)



# from nltk.sentiment import SentimentIntensityAnalyzer
# import nltk
# import telebot

# nltk.download('vader_lexicon')
# sia = SentimentIntensityAnalyzer()

# # Function to analyze sentiment
# def analyze_sentiment_nltk(text):
#     sentiment = sia.polarity_scores(text)
#     if sentiment["compound"] > 0:
#         return "😊 Positive"
#     elif sentiment["compound"] < 0:
#         return "😠 Negative"
#     else:
#         return "😐 Neutral"

# # Telegram command for sentiment analysis
# @bot.message_handler(commands=['sentiment'])
# def sentiment_command(message):
#     text = message.text.replace("/sentiment", "").strip()
#     if not text:
#         bot.reply_to(message, "Please provide some text to analyze. Example: `/sentiment I love this bot!`")
#         return
#     sentiment_result = analyze_sentiment_nltk(text)
#     bot.reply_to(message, f"Sentiment Analysis Result: {sentiment_result}")

# bot.polling()




if __name__ == "__main__":
    bot.polling(none_stop=True)
