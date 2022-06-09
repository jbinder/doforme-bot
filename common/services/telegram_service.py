from logging import Logger

import telegram
from telegram.utils.helpers import escape_markdown

from components.user.user_service import UserService


class TelegramService:

    logger: Logger
    user_service: UserService

    def __init__(self, user_service, logger):
        self.user_service = user_service
        self.logger = logger

    def get_chat_users(self, bot, chat_id):
        """ :returns a list of tuples containing id and name of users of the specified chat """
        return [(user_id, self.get_user_name(bot, chat_id, user_id))
                for user_id in self.user_service.get_chat_users(chat_id)]

    def get_chats(self, bot, user_id):
        """ :returns a list of tuples containing id and name of chats of the specified user """
        chats = []
        for chat_id in self.user_service.get_chats_of_user(user_id):
            chats.append((chat_id, bot.getChat(chat_id).title))
        return chats

    def get_user_name(self, bot, chat_id, user_id):
        user_name = 'unknown'
        try:
            user_name = bot.getChatMember(chat_id, user_id).user.name
        except Exception:
            self.logger.exception(f"Unable to get username (chat/user): {chat_id}/{user_id}.")
        return user_name

    def get_mention(self, bot, chat_id, user_id):
        """
        Warning: This is only shown correctly in messages with parse_mode=telegram.ParseMode.MARKDOWN!
        :returns A link to the specified user ('mention') in Markdown format, e.g. "@user1"
        """
        user_name = self.get_user_name(bot, chat_id, user_id)
        return f"[{user_name}](tg://user?id={user_id})"

    @staticmethod
    def is_private_chat(update):
        return update.message.chat.type == 'private'

    @staticmethod
    def remove_inline_keybaord(bot, query):
        bot.edit_message_text(text=query.message.text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=None
                              )

    @staticmethod
    def send_message(bot, user_id, text, parse_mode: telegram.ParseMode=telegram.ParseMode.HTML,
                     reply_markup=None, skip_escaping=False):
        if parse_mode is telegram.ParseMode.MARKDOWN and not skip_escaping:
            text = TelegramService.escape_text(text)
        bot.send_message(user_id, text, parse_mode=parse_mode, reply_markup=reply_markup)

    @staticmethod
    def send_reply(message: telegram.message, text, reply_markup=None, quote=False,
                   parse_mode: telegram.ParseMode=telegram.ParseMode.HTML, skip_escaping=False):
        if parse_mode is telegram.ParseMode.MARKDOWN and not skip_escaping:
            text = TelegramService.escape_text(text)
        message.reply_text(text, reply_markup=reply_markup, quote=quote, parse_mode=parse_mode)

    @staticmethod
    def escape_text(text: str):
        return escape_markdown(text)
