"""
main module
entry point for messages
"""

import logging
import time
import asyncio

from prometheus_client import Counter
from prometheus_async.aio.web import start_http_server_in_thread
import aiohttp

# TODO: dynamically import plugins
from .plugins import pins

from .config import config
from .message import Message
from .api import TelegramAPI, TelegramError
from .storage import RedisStorage
from .plugin import registry
from .language import language_context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


SKIP_COUNT = Counter("gb_updates_skipped", "updates skipped by gb for being too old")
UPDATE_COUNT = Counter("gb_updates", "updates received by gb", ["type"])
PLUGIN_DURATION = Counter("gb_plugin_time_seconds",
                          "duration of plugin processing", ["plugin"])

class Bot:
    """The Bot class contains the top-level state of the bot, such as database
    connections, tokens,
    etc"""
    def __init__(self, config_):
        self.config = config_
        self.tgapi = TelegramAPI(token=config.token)
        self.storage = RedisStorage("redis://localhost/2")

    async def on_msg_received(self, message: Message):
        """handler called when a message is received"""

        now = time.time()
        if message["date"] < now - self.config.old_update_threshold:
            SKIP_COUNT.inc()
            logging.warning("old update skipped: %s", now - message["date"])
            return

        await self.storage.set_language(message.chat_id, "de_DE")
        chat_language = await self.storage.get_language(message.chat_id)
        # set the language context variable to the chat language
        # this value will be set in all functions called from this function
        language_context.set(chat_language)

        if message.chat_type == "group":
            # TODO: insert regular group handling
            pass

        """
        await self.tgapi.respond_to_sender_in_pm(
            message, "hi!",
            reply_markup={"inline_keyboard": [[{"text": "test", "callback_data":
                                               "test123"}]]}
        )
        """
        # TODO: insert channel handling
        # TODO: collect/cache username info

        # TODO: plugin logic
        handler = registry.get_command_handler("setpin")

        if handler is None:
            await self.tgapi.respond_to(message, "invalid command")
            return

        await handler(self, message)


    async def on_callback_query_received(self, callback: dict):
        """handler called when a callback query is received"""
        print("callback")

    async def on_update_received(self, update: dict):
        """handler called when a message is received"""

        if "callback_query" in update:
            UPDATE_COUNT.labels("callback_query").inc()
            await self.on_callback_query_received(update["callback_query"])
        elif "message" in update:
            UPDATE_COUNT.labels("message").inc()
            await self.on_msg_received(Message(update["message"], None))
        else:
            UPDATE_COUNT.labels("other").inc()
            logger.warning("invalid update type: %s", update)

    async def start(self):
        """start the bot, (in polling mode for now)"""
        logger.info("starting bot...")
        await self.tgapi.init()
        try:
            await self.storage.init()
        except IOError:
            logger.exception("failed to connect to redis")
            return

        try:
            api_me = await self.tgapi.getMe()
        except TelegramError:
            logger.exception("getMe failed... Is your Bot token valid?")
            return
        except aiohttp.ClientError:
            logger.error("failed to connect to api endpoint...")
            return
        logger.info("running as %s", api_me["username"])

        await self.polling_loop()

    async def polling_loop(self):
        """Task that continues polling the API forever"""
        offset = 0
        while True:
            updates = await self.tgapi.getUpdates(timeout=120, offset=offset)
            for update in updates:
                print(update)
                await self.on_update_received(update)
                offset = update["update_id"] + 1

def main():
    """main entry point"""
    start_http_server_in_thread(port=9500)
    bot = Bot(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.start())
