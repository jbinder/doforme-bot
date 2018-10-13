from telegram.ext import Dispatcher

from common.component_base import ComponentBase
from common.event_type import EventType
from components.announce.announce_command_handler import AnnounceCommandHandler


class AnnounceComponent(ComponentBase):

    command_handler: AnnounceCommandHandler

    def __init__(self, command_handler: AnnounceCommandHandler):
        super().__init__()
        self.command_handler = command_handler

    def init(self, dp: Dispatcher):
        cmd_handlers = [
            ('admin-announce', self.command_handler.admin_announce, False),
        ]
        super()._register_command_handlers(dp, cmd_handlers)

    def register_observer(self, event_type: EventType, observer: callable):
        raise NotImplementedError()
