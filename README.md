# Telegram AI Chatbot with Gemini & MongoDB

This is a Telegram AI Chatbot powered by Google Gemini AI and MongoDB. It supports:

> ✅ User Registration (Stores user details in MongoDB)✅ AI-Powered Chat (Handles queries via Gemini API)✅ Image & File Analysis (Analyzes media using Gemini AI)✅ Web Search (Provides summarized results)

# 📌 Installation & Setup

## 1️⃣ Clone the Repository

```
git clone https://github.com/fx818/TelegramBot.git
cd TelegramBot
```

## 2️⃣ Create a Virtual Environment (Optional but Recommended)

```
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

## 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

## 4️⃣ Set Up Environment Variables

Create a .env file in the project directory and add:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
MONGO_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

`🔹 Setup Telegram Bot`

Go to BotFather on Telegram.

Create a new bot using /newbot.

Copy the bot token and paste it into .env as `TELEGRAM_BOT_TOKEN`.

`🔹 Setup MongoDB Database`

Create a MongoDB Atlas account.

Create a new database and get the connection string.

Paste it into .env as `MONGO_URI`.

`🔹 Setup Gemini AI API`

Go to Google AI Studio and generate an API key.

Paste it into .env as `GEMINI_API_KEY`.

## 🚀 Run the Bot`

```
python bot.py
```

## 📌 Features & Functionality

### ✅ User Registration

When a user starts the bot, they are automatically registered.

Their chat ID, username, and first name are stored in MongoDB.

### ✅ AI-Powered Chat

Users can send messages to get AI-powered responses via Gemini API.

### ✅ Image & File Analysis

Users can send images or documents, and the bot will analyze them.

Uses gemini-1.5-flash for image processing.

Uses gemini-1.5-pro for document analysis.

### ✅ Web Search

Users can search for information via the bot.

The bot will fetch summarized results and top links.

### ✅ Sentiment Analysis

Users can give a sentence and check for the sentiment of that sentence.

'/sentiment your_sentence'.
