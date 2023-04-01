from logging import Logger
from typing import List

import telegram
from telegram.error import ChatMigrated
from telegram.utils.helpers import escape_markdown

from common.migration_handler_base import MigrationHandlerBase
from components.user.user_service import UserService


class TelegramService:

    logger: Logger
    user_service: UserService
    migration_handlers: List[MigrationHandlerBase]

    def __init__(self, user_service, logger, migration_handlers: List[MigrationHandlerBase]):
        self.user_service = user_service
        self.logger = logger
        self.migration_handlers = migration_handlers

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
        if user_id == 0 and chat_id != 0:
            return 'anyone'
        try:
            user_name = bot.getChatMember(chat_id, user_id).user.name
        except ChatMigrated as e:
            self.logger.exception(f"Chat has been migrated to Supergroup (chat/user): {chat_id}/{user_id}.")
            try:
                # migrate to the supergroup
                [handler.migrate_to_supergroup(chat_id, e.new_chat_id) for handler in self.migration_handlers]
                user_name = bot.getChatMember(e.new_chat_id, user_id).user.name
            except Exception:
                self.logger.exception(f"Unable to get username (chat/user): {chat_id}/{user_id}.")
        except Exception:
            self.logger.exception(f"Unable to get username (chat/user): {chat_id}/{user_id}.")
        return user_name

    def get_mention(self, bot, chat_id, user_id):
        """
        Warning: This is only shown correctly in messages with parse_mode=telegram.ParseMode.MARKDOWN!
        :returns A link to the specified user ('mention') in Markdown format, e.g. "@user1"
        """
        if user_id == 0:
            return 'anyone in here'
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

    def send_message(self, bot, user_id, text, parse_mode: telegram.ParseMode=telegram.ParseMode.HTML,
                     reply_markup=None, skip_escaping=False):
        if parse_mode is telegram.ParseMode.MARKDOWN and not skip_escaping:
            text = TelegramService.escape_text(text)
        try:
            bot.send_message(user_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
            return True
        except Exception:
            self.logger.exception(f"Unable to send message to user: {user_id}.")
            return False

    def send_reply(self, message: telegram.message, text, reply_markup=None, quote=False,
                   parse_mode: telegram.ParseMode=telegram.ParseMode.HTML, skip_escaping=False):
        if parse_mode is telegram.ParseMode.MARKDOWN and not skip_escaping:
            text = TelegramService.escape_text(text)
        try:
            message.reply_text(text, reply_markup=reply_markup, quote=quote, parse_mode=parse_mode)
            return True
        except Exception:
            self.logger.exception(f"Unable to send reply to user.")
            return False

    @staticmethod
    def escape_text(text: str):
        return escape_markdown(text)
