from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import ChatType, ParseMode
import logging
import argparse
import asyncio
import pandas as pd
import re


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--bot_key', type=str, default='', help='Telegram bot key')
    return parser.parse_args()


async def start_handler(event: types.Message):
    await event.answer(
        f"Hello, {event.from_user.get_mention(as_html=True)} 👋!",
        parse_mode=types.ParseMode.HTML,
    )

async def main(BOT_TOKEN):
    bot = Bot(token=BOT_TOKEN)
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        await disp.start_polling()
    finally:
        await bot.close()

class BotInstance(object):
    def __init__(self, bot_token):
        # Configure Bot and Dispatcher
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher(self.bot)
        logging.info("Bot set with token %s", bot_token)



    def start(self):

        # Register handlers
        self.dp.register_message_handler(self.query_ama_record_private,
                                         chat_type=[ChatType.PRIVATE],
                                         commands={"ama"})
        self.dp.register_message_handler(self.send_welcome_private,
                                         chat_type=[ChatType.PRIVATE],
                                         commands={"start"})
        self.dp.register_message_handler(self.ama_howto_public,
                                         chat_type=[ChatType.PRIVATE, ChatType.SUPERGROUP],
                                         commands={"ama_howto"})

        # Load data
        self.ama_df = pd.read_csv('data/NULink_AMA_1204.csv', dtype=str, na_filter=False)

        executor.start_polling(self.dp)

    async def query_ama_record_public(self, message: types.Message):
        logging.debug(message)
        message.text



    async def query_ama_record_private(self, message: types.Message):
        logging.debug(message)
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_list = re.findall(email_regex, message.text)

        for cur_email in email_list:
            reply_str = '```\n' + self.ama_df.loc[self.ama_df.email == cur_email,:].to_string() + '\n```'
            await message.reply(reply_str, parse_mode=ParseMode.MARKDOWN_V2)


    async def ama_howto_public(self, message: types.Message):
        """
        This handler will be called when user sends message in private chat or supergroup
        """
        await message.reply("You can DM @NULinkHelper\_bot to query AMA records using your email \n" +
                            "你可以跟 @NULinkHelper\_bot 私聊来用填表时的电子邮箱查询AMA记录 \n",
                            parse_mode=ParseMode.MARKDOWN_V2)

        # propagate message to the next handler
        raise SkipHandler

    async def send_welcome_private(self, message: types.Message):
        """
        This handler will be called when user sends message in private chat or supergroup
        """
        await message.reply("Hi, please use `/ama <emails, separated by space>` to query ama record \n" +
                            "e\.g\. `/ama test@test.com` \n" +
                            "请使用 `/ama <填表时候的电子邮箱, 如果有多个请用空格分开>` 命令来查询AMA记录 \n" +
                            "比如： `/ama test@test.com` \n",
                            parse_mode=ParseMode.MARKDOWN_V2)

        # propagate message to the next handler
        raise SkipHandler


    async def send_welcome_public(self, message: types.Message):
        """
        This handler will be called when user sends message in private chat
        """
        await message.reply("Hi!\nI'm hearing your messages only in private chats")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = parse_args()
    bot_token = args.bot_key

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Setup bot
    instance = BotInstance(bot_token)
    instance.start()
