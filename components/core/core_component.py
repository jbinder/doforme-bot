from telegram.ext import Dispatcher

from common.component_base import ComponentBase
from common.event_type import EventType
from components.core.core_command_handler import CoreCommandHandler


class CoreComponent(ComponentBase):

    command_handler: CoreCommandHandler

    def __init__(self, command_handler: CoreCommandHandler):
        super().__init__()
        self.command_handler = command_handler

    def init(self, dp: Dispatcher):
        cmd_handlers = [
            ('start', self.command_handler.help_show, False),
            ('help', self.command_handler.help_show, False),
        ]
        super()._register_command_handlers(dp, cmd_handlers)

    def register_observer(self, event_type: EventType, observer: callable):
        raise NotImplementedError()
