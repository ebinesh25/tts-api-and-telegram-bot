import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the bot token from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://0.0.0.0:8000/upload/article"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi! Send me a multi-line message and I will process it.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    raw_text = update.message.text
    logger.info(f"Received message from {update.message.from_user.name}")

    await update.message.reply_text("Processing your request...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json={"raw_text": raw_text}, timeout=120.0)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            logger.info(f"API Response Status Code: {response.status_code}")

            api_response = response.json()
            reply_text = api_response['url']
            logger.info(f"API Response Content: {reply_text}")
            await update.message.reply_text(f"{reply_text}")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        await update.message.reply_text(f"Error: Failed to process your request. The API returned a status of {e.response.status_code}.")
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        await update.message.reply_text("Error: Could not connect to the API. Please make sure the API server is running.")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        logger.error(f"Response content that failed to parse: {response.text}")
        await update.message.reply_text("Error: The API returned a response that could not be understood.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in .env file. Please add it.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - handle the message from Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
