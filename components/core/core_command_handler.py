from common.command_handler_base import CommandHandlerBase
from common.decorators.show_typing import show_typing
from components.core.core_event_type import CoreEventType


class CoreCommandHandler(CommandHandlerBase):

    def __init__(self, admin_id, callbacks, texts, telegram_service):
        super().__init__(admin_id, callbacks, texts, telegram_service)

    @show_typing
    def help_show(self, bot, update):
        update.message.reply_text(self.texts['help'])

    @show_typing
    def start(self, bot, update):
        self.notify_observers(CoreEventType.USER_REGISTERED, {'user_id': update.effective_user.id})
        self.help_show(bot, update)
