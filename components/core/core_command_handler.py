from common.command_handler_base import CommandHandlerBase
from common.decorators.show_typing import show_typing


class CoreCommandHandler(CommandHandlerBase):

    def __init__(self, admin_id, texts, telegram_service):
        super().__init__(admin_id, texts, telegram_service)

    @show_typing
    def help_show(self, bot, update):
        update.message.reply_text(self.texts['help'])
