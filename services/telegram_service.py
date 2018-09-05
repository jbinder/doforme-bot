class TelegramService:
    def __init__(self, user_service):
        self.user_service = user_service

    def get_chat_users(self, bot, chat_id):
        """ :returns a list of tuples containing id and name of users of the specified chat """
        return [(user_id, bot.getChatMember(chat_id, user_id).user.name)
                for user_id in self.user_service.get_chat_users(chat_id)]

    def get_chats(self, bot, user_id):
        """ :returns a list of tuples containing id and name of chats of the specified user """
        chats = []
        for chat_id in self.user_service.get_chats_of_user(user_id):
            chats.append((chat_id, bot.getChat(chat_id).title))
        return chats

    @staticmethod
    def get_mention(bot, chat_id, user_id):
        """
        Warning: This is only shown correctly in messages with parse_mode=telegram.ParseMode.MARKDOWN!
        :returns A link to the specified user ('mention') in Markdown format, e.g. "@user1"
        """
        user_name = bot.getChatMember(chat_id, user_id).user.name
        return f"[{user_name}](tg://user?id={user_id})"
