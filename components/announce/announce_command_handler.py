from common.command_handler_base import CommandHandlerBase
from common.decorators.show_typing import show_typing
from components.user.user_service import UserService


class AnnounceCommandHandler(CommandHandlerBase):

    user_service: UserService

    def __init__(self, admin_id, callbacks, texts, telegram_service, user_service):
        super().__init__(admin_id, callbacks, texts, telegram_service)
        self.user_service = user_service

    @show_typing
    def admin_announce(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        text = update.message.text[len("/admin-announce"):].strip()
        if len(text) < 1:
            update.message.reply_text(self.texts['missing-text'](self.texts['admin']))
            return
        users = self.user_service.get_all_users()
        message = f"{self.texts['announcement-prefix']}\n{text}\n\n{self.texts['feedback-reply-postfix']}"
        num_success = 0
        num_failed = 0
        for user_id in users:
            if self.telegram_service.send_message(bot, user_id, message):
                num_success += 1
            else:
                num_failed += 1
        self.telegram_service.send_reply(update.message, self.texts['announcement-sent'](num_success, num_failed))
