from telegram.ext import Dispatcher, Filters

from common.component_base import ComponentBase
from common.event_type import EventType
from components.user.user_command_handler import UserCommandHandler


class UserComponent(ComponentBase):

    command_handler: UserCommandHandler

    def __init__(self, command_handler: UserCommandHandler):
        super().__init__()
        self.command_handler = command_handler

    def init(self, dp: Dispatcher):
        msg_handlers = [
            (Filters.status_update.new_chat_members, self.command_handler.chat_member_add),
            (Filters.status_update.left_chat_member, self.command_handler.chat_member_remove),
            (Filters.text, self.command_handler.chat_member_add)
        ]
        super()._register_message_handlers(dp, msg_handlers)

    def register_observer(self, event_type: EventType, observer: callable):
        self.command_handler.register_observer(event_type, observer)
