from telegram.ext import Dispatcher

from common.component_base import ComponentBase
from components.feedback.feedback_command_handler import FeedbackCommandHandler
from components.feedback.feedback_service import FeedbackService
from components.feedback.texts import texts


class FeedbackComponent(ComponentBase):

    command_handler: FeedbackCommandHandler
    feedback_service: FeedbackService

    def __init__(self, admin_id: int):
        super().__init__()
        self.feedback_service = FeedbackService()
        self.command_handler = FeedbackCommandHandler(admin_id, texts, self.feedback_service)

    def init(self, dp: Dispatcher):
        cmd_handlers = [
            ('feedback', self.command_handler.feedback_add, False),
            ('admin-feedback-show', self.command_handler.admin_feedback_show, False),
            ('admin-feedback-reply', self.command_handler.admin_feedback_reply, False),
            ('admin-feedback-close', self.command_handler.admin_feedback_close, False),
        ]
        super()._register_commands(dp, cmd_handlers)

    def get_stats(self):
        return self.feedback_service.get_stats()
