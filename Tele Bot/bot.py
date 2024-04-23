import asyncio
import logging
import threading
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, Application

class Telegram_bot():
    def __init__(self, token: str):
        # Build the Bot
        self.application = Application.builder().token(token).build()
        self.__bot_status__ = True

        # Add command Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, self.handle_reply_with_images))

        # Create a event loop for running bot
        self.loop = asyncio.new_event_loop()

       # Start the bot in a separate task
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()

        # Setup logging
        logging.basicConfig(level=logging.WARN ,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger("Telegram_bot")
        self.logger.warning("The Bot was successfully created and is now running.")

    async def __bot_start_handler__(self):
        application = self.application

        # start The bot using PTB setup
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        status = self.__bot_status__
        while status:
            status = self.__bot_status__
            await asyncio.sleep(10)

    async def __bot_stop_handler__(self):
        application = self.application

        # Stop The bot using PTB setup
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

    async def __bot_start__(self):
        # Create the starting task and wait for it to finish
        start_task = asyncio.create_task(self.__bot_start_handler__())

        try:
            # since the task contains an infinite loop the bot will stay awake
            await start_task
        except KeyboardInterrupt:
            # stop the bot if interuptted
            self.logger.warning("Program interrupted by user.")
            await self.__bot_stop_handler__()

        # stop the bot
        await self.__bot_stop_handler__()
        self.__bot_status__ = True
        self.logger.warning("the bot was stopped.")

    def run_bot(self):
        # Create a new event loop and run the bot forever
        self.loop.create_task(self.__bot_start__())
        self.loop.run_forever()

    def stop_bot(self):
        self.__bot_status__ = False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm a bot created by and for Prithvi.")
    
    def send_msg(self, text: str, send_to: int):
        asyncio.run_coroutine_threadsafe(self.__send_msg__(text, send_to), self.loop)

    async def __send_image__(self, image: str, send_to: int, caption: str = ""):
        await self.application.bot.send_photo(send_to, image, caption)

    def send_image(self, image: str, send_to: int, caption: str = ""):
        asyncio.run_coroutine_threadsafe(self.__send_image__(image, send_to, caption))

    async def __send_audio__(self, audio: str, send_to: int):
        await self.application.bot.send_audio(send_to, audio)

    def send_audio(self, audio: str, send_to: int):
        asyncio.run_coroutine_threadsafe(self.__send_audio__(audio, send_to), self.loop)
