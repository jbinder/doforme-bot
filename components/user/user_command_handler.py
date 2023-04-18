from common.command_handler_base import CommandHandlerBase
from common.common_event_type import CommonEventType
from components.user.user_event_type import UserEventType

from components.core.core_event_type import CoreEventType
from components.user.user_service import UserService


class UserCommandHandler(CommandHandlerBase):

    bot_name: str
    user_service: UserService

    def __init__(self, admin_id, callbacks, texts, telegram_service, bot_name, user_service):
        super().__init__(admin_id, callbacks, texts, telegram_service)
        self.bot_name = bot_name
        self.user_service = user_service
        self.register_observer(
            CoreEventType.USER_REGISTERED,
            lambda event: self.user_service.add_user_if_not_exists(event['user_id']))
        self.register_observer(
            CommonEventType.USER_SEND_FAILED,
            lambda event: self.user_service.report_user_send_failure(event))
        self.register_observer(
            CommonEventType.CHAT_SEND_FAILED,
            lambda event: self.user_service.report_chat_send_failure(event))

    def chat_member_add(self, bot, update):
        chat_id = update.message.chat.id

        for member in update.message.new_chat_members:
            # register in group chats
            if not member.is_bot:
                self._register_user_chat(chat_id, member, update)
            # register bot
            elif member.username == self.bot_name:
                self.user_service.add_chat_if_not_exists(chat_id)
                update.message.reply_text(self.texts['welcome-bot'])

        if len(update.message.new_chat_members) < 1:
            # register in private chat
            if update.effective_chat.type == "private":
                self.user_service.add_user_if_not_exists(update.effective_user.id)
                if len(self.user_service.get_chats_of_user(update.effective_user.id)) < 1:
                    update.message.reply_text(self.texts['add-to-group'])
                else:
                    update.message.reply_text(self.texts['help'])
            # register in group chats (alternative)
            else:
                self._register_user_chat(chat_id, update.effective_user, update)

    def chat_member_remove(self, bot, update):
        chat_id = update.message.chat_id
        user_id = update.message.left_chat_member.id
        # delete chat user
        if self.user_service.remove_user_chat_if_exists(user_id, chat_id):
            # TODO: show deleted tasks?
            self.notify_observers(UserEventType.USER_LEFT_CHAT, {'user_id': user_id, 'chat_id': chat_id})
            update.message.reply_text(self.texts['user-goodbye'](update.message.left_chat_member.first_name))
        # delete chat if no users remain
        if len(self.user_service.get_chat_users(chat_id)) == 0:
            self.user_service.remove_chat_if_exists(chat_id)

    def _register_user_chat(self, chat_id, member, update):
        if self.user_service.add_user_chat_if_not_exists(member.id, chat_id):
            update.message.reply_text(self.texts['user-welcome'](update.message.chat.title, member.first_name) +
                                      "\n\n" + self.texts['help'])
