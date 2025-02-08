import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from lastfm_request import LastFMClient

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class LastFMBot:
    """Telegram bot that fetches top tracks and artists from Last.fm."""

    def __init__(self):
        """Initialize the bot with API keys and username."""
        api_key = os.getenv("LASTFM_API_KEY")
        user = os.getenv("LASTFM_USERNAME")
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not api_key or not telegram_token or not user:
            logging.error("API keys or username not set in environment variables.")
            raise ValueError("API keys not set in environment variables.")

        self.lastfm_client = LastFMClient(api_key, user) # lastfm client instance
        self.application = Application.builder().token(telegram_token).build() # telegram bot application
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler(
            ["monthartists", "monthtracks", "weekartists", "weektracks" ,"alltime"], 
            self.fetch_lastfm_command
        ))
        self.application.add_handler(CommandHandler("nowplaying", self.now_playing_command))
        #to handle not / commands
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_commands))

    async def now_playing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fetch and reply with the currently playing track."""
        data = await self.lastfm_client.fetch_now_playing()
        await update.message.reply_text(data)

    async def fetch_lastfm_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generic handler for fetching top tracks or artists."""
        command = update.message.text.strip().lstrip('/')
        logging.info(f"Processing command: {command}")

        period_mapping = {"month": "1month", "week": "7day"}
        item_mapping = {"artists": "user.gettopartists", "tracks": "user.gettoptracks"}

        for period_key, period in period_mapping.items():
            if period_key in command:
                for item_key, method in item_mapping.items():
                    if item_key in command:
                        await self.fetch_and_reply(update, method, period)
                        return
        
        await update.message.reply_text("Invalid command format. Use /help to see available commands.")

    async def fetch_and_reply(self, update: Update, method: str, period: str, num_items: int = 10):
        """Fetch and send formatted Last.fm data."""
        item_type = "tracks" if "track" in method else "artists"

        data = await self.lastfm_client.fetch_data(method, period, num_items)
        if data:
            message = self.lastfm_client.format_data(data, item_type, num_items, period)
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Failed to fetch data. Please try again later.")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a help message when /help is issued."""
        await update.message.reply_text(
            "This bot fetches your data from Last.fm.\n\n"
            "Commands:\n"
            "/monthartists - Get top artists for the current month\n"
            "/monthtracks - Get top tracks for the current month\n"
            "/weekartists - Get top artists for the current week\n"
            "/weektracks - Get top tracks for the current week\n"
            #"/fa - Get top tracks and artists of all time\n"
            "/nowplaying - Get the track that is currently playing\n"
            "/help - Display this help message"
        )

    async def handle_text_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input as commands (e.g., 'help' instead of '/help')."""
        text = update.message.text.lower().strip()

        command_map = {
            "help": self.help_command,
            "month artists": lambda u, c: self.fetch_and_reply(u, "user.gettopartists", "1month"),
            "month tracks": lambda u, c: self.fetch_and_reply(u, "user.gettoptracks", "1month"),
            "week artists": lambda u, c: self.fetch_and_reply(u, "user.gettopartists", "7day"),
            "week tracks": lambda u, c: self.fetch_and_reply(u, "user.gettoptracks", "7day"),
            #"alltime": lambda u, c: self.fetch_and_reply(u, "user.gettoptracks", "overall"),
            "nowplaying": self.now_playing_command,
        }

        if text in command_map:
            await command_map[text](update, context)
        else:
            await update.message.reply_text("Unknown command. Try /help for available commands.")

    def run(self):
        """Start the bot."""
        self.application.run_polling()