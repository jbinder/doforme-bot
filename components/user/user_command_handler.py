from common.command_handler_base import CommandHandlerBase
from components.user.user_event_type import UserEventType
from components.user.user_service import UserService


class UserCommandHandler(CommandHandlerBase):

    bot_name: str
    user_service: UserService

    def __init__(self, admin_id, texts, bot_name, user_service):
        super().__init__(admin_id, texts)
        self.bot_name = bot_name
        self.user_service = user_service

    def chat_member_add(self, bot, update):
        chat_id = update.message.chat.id
        for member in update.message.new_chat_members:
            if not member.is_bot:
                self._register_user(chat_id, member, update)
            if member.username == self.bot_name:
                update.message.reply_text(self.texts['welcome-bot'])
        if len(update.message.new_chat_members) < 1:
            if update.effective_chat.type == "private":
                if len(self.user_service.get_chats_of_user(update.effective_user.id)) < 1:
                    update.message.reply_text(self.texts['add-to-group'])
                else:
                    update.message.reply_text(self.texts['help'])
            else:
                self._register_user(chat_id, update.effective_user, update)

    def chat_member_remove(self, bot, update):
        chat_id = update.message.chat_id
        user_id = update.message.left_chat_member.id
        if self.user_service.remove_user_chat_if_exists(user_id, chat_id):
            # TODO: show deleted tasks?
            self.notify_observers(UserEventType.USER_LEFT_CHAT, {'user_id': user_id, 'chat_id': chat_id})
            update.message.reply_text(self.texts['user-goodbye'](update.message.left_chat_member.first_name))

    def _register_user(self, chat_id, member, update):
        if self.user_service.add_user_chat_if_not_exists(member.id, chat_id):
            update.message.reply_text(self.texts['user-welcome'](update.message.chat.title, member.first_name) +
                                      "\n\n" + self.texts['help'])
