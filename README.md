# GhoncheSummerizer Bot

A Telegram bot that summarizes group chat messages using Google's Gemini AI with a humorous, friendly twist. Created specifically for FARHAN with love! 😈

## Features

- **Message Summarization**: Generates witty, sarcastic summaries of recent chat messages
- **Customizable Summary Length**: Use `/summary [number]` to specify how many messages to summarize (max 500)
- **Reply Tracking**: Identifies and highlights the most replied-to messages
- **Persistent Storage**: Saves all messages to a local SQLite database
- **Humorous Style**: Summaries are written in a playful, teasing manner without being offensive

## Requirements

- Python 3.7+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/tel-py.git
   cd tel-py
   ```

2. Install dependencies:
   ```bash
   pip install python-telegram-bot google-generativeai python-dotenv
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

1. Run the bot:
   ```bash
   python main.py
   ```

2. Add the bot to your Telegram group as an administrator

3. Use the following commands:
   - `/start` - Welcome message
   - `/summary` - Summarize the last 100 messages
   - `/summary [number]` - Summarize the last N messages (max 500)

## How It Works

- The bot listens to all text messages in the group and stores them in a SQLite database
- When `/summary` is called, it fetches the specified number of recent messages
- Messages are processed in chunks of 20 for optimal performance
- Each chunk is summarized using Gemini AI with a prompt that creates humorous, personalized descriptions for each user
- If multiple chunks exist, they're combined into a final comprehensive summary
- The bot also identifies the top 5 most replied-to messages and includes them in the summary

## Database

The bot uses SQLite (`messages.db`) to store:
- Chat ID
- Username
- Message text
- Message ID
- Reply-to message ID (for tracking replies)

## Configuration

- `TELEGRAM_TOKEN`: Your Telegram bot token
- `GEMINI_API_KEY`: Your Google Gemini API key
- `DB_PATH`: Database file path (default: "messages.db")

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Please use responsibly and have fun! 🎉
