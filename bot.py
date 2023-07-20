import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext, CallbackQueryHandler, MessageHandler, filters 
#import telegram.ext.filters as Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,  CallbackQuery
from manager import  InfoBot
import configparser
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
chatbot = InfoBot('config.ini')
config = configparser.ConfigParser()
config.read('config.ini')

# Intent Classification
section = config['telegram']
key = section.get('key', fallback=None)
        

async def reply_to_message(update: Update, context: CallbackContext) -> None:
    """Reply to a normal message."""
    # Implement your logic here to handle normal messages
    # You can access the message text using update.message.text
    reply = chatbot.reply(update.message.text)
    await update.message.reply_text(str(reply))


def main() -> None:
    """Start the bot and the length checking task."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(key).build()

    # Add command handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
