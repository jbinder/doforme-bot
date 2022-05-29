from logging import Logger

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
