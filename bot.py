import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from lastfm_request import format_data, fetch_lastfm_data


# Load environment variables
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])

lastfm_api_key = os.getenv('LASTFM_API_KEY')
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
your_lastfm_username = os.getenv('LASTFM_USERNAME')

if not lastfm_api_key or not telegram_bot_token or not your_lastfm_username:
    logging.error("API keys or username not set in environment variables.")
    raise ValueError("API keys not set in environment variables.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    logging.info(f"User {update.effective_user.id} started the bot.")
    await update.message.reply_text("Welcome! Use /help to see the available commands.")

async def fetch_and_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str, period: str, num_items: int = 10):
    """
    Generic function to fetch and send data from Last.fm.
    
    Args:
        update: Telegram update object.
        context: Telegram context object.
        method: Last.fm API method to call ('user.gettopartists' or 'user.gettoptracks').
        period: Time period (e.g., '1month', '7day').
        num_items: Number of items to fetch (default is 10).
    """
    logging.info(f"Fetching data using method '{method}' for period '{period}'.")

    # Determine item type based on the method
    if method == "user.gettoptracks":
        item_type = "tracks"
    elif method == "user.gettopartists":
        item_type = "artists"
    else:
        await update.message.reply_text("Invalid method specified.")
        return

    # Fetch data from Last.fm
    user = your_lastfm_username
    data = await fetch_lastfm_data(user, method, api_key=lastfm_api_key, period=period, limit=num_items)

    # Check if data was fetched and format it
    if data:
        formatted_message = format_data(data, item_type=item_type, num_items=int(num_items), period=period)
        await update.message.reply_text(formatted_message)
    else:
        await update.message.reply_text("Failed to fetch data. Please try again later.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    logging.info("User requested help.")
    await update.message.reply_text(
        "This bot fetches top tracks and artists from Last.fm.\n\n"
        "Commands:\n"
        "/start - A welcome message is printed\n"
        "/monthartist - Get top artists for the current month\n"
        "/monthtrack - Get top tracks for the current month\n"
        "/weekartist - Get top artists for the current week\n"
        "/weektrack - Get top tracks for the current week\n"
        "/help - Display this help message"
    )

def main():
    application = Application.builder().token(telegram_bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler(
        "monthartist",
        lambda update, context: fetch_and_reply(update, context, "user.gettopartists", "1month", num_items=10)
    ))
    application.add_handler(CommandHandler(
        "monthtrack",
        lambda update, context: fetch_and_reply(update, context, "user.gettoptracks", "1month", num_items=10)
    ))
    application.add_handler(CommandHandler(
        "weekartist",
        lambda update, context: fetch_and_reply(update, context, "user.gettopartists", "7day", num_items=10)
    ))
    application.add_handler(CommandHandler(
        "weektrack",
        lambda update, context: fetch_and_reply(update, context, "user.gettoptracks", "7day", num_items=10)
    ))

    application.run_polling()

if __name__ == '__main__':
    main()
