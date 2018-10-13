from telegram.ext import Dispatcher, Filters

from common.component_base import ComponentBase
from common.event_type import EventType
from components.user import texts
from components.user.user_command_handler import UserCommandHandler
from components.user.user_service import UserService


class UserComponent(ComponentBase):

    command_handler: UserCommandHandler
    user_service: UserService

    def __init__(self, admin_id: int, bot_name: str):
        super().__init__()
        self.user_service = UserService()
        self.command_handler = UserCommandHandler(admin_id, texts, bot_name, self.user_service)

    def init(self, dp: Dispatcher):
        msg_handlers = [
            (Filters.status_update.new_chat_members, self.command_handler.chat_member_add),
            (Filters.status_update.left_chat_member, self.command_handler.chat_member_remove),
            (Filters.text, self.command_handler.chat_member_add)
        ]
        super()._register_message_handlers(dp, msg_handlers)

    def get_stats(self):
        raise NotImplementedError()

    def register_observer(self, event_type: EventType, observer: callable):
        self.command_handler.register_observer(event_type, observer)

    def get_user_service(self):
        return self.user_service
