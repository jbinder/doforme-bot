from telegram.ext import Dispatcher

from common.component_base import ComponentBase
from common.event_type import EventType
from components.feedback.feedback_command_handler import FeedbackCommandHandler


class FeedbackComponent(ComponentBase):

    command_handler: FeedbackCommandHandler

    def __init__(self, command_handler: FeedbackCommandHandler):
        super().__init__()
        self.command_handler = command_handler

    def init(self, dp: Dispatcher):
        cmd_handlers = [
            ('feedback', self.command_handler.feedback_add, False),
            ('admin-feedback-show', self.command_handler.admin_feedback_show, False),
            ('admin-feedback-reply', self.command_handler.admin_feedback_reply, False),
            ('admin-feedback-close', self.command_handler.admin_feedback_close, False),
        ]
        super()._register_command_handlers(dp, cmd_handlers)

    def register_observer(self, event_type: EventType, observer: callable):
        raise NotImplementedError()
