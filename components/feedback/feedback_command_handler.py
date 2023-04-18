from common.command_handler_base import CommandHandlerBase
from components.feedback.feedback_service import FeedbackService
from common.decorators.show_typing import show_typing


class FeedbackCommandHandler(CommandHandlerBase):

    feedback_service: FeedbackService

    def __init__(self, admin_id, callbacks, texts, telegram_service, feedback_service):
        super().__init__(admin_id, callbacks, texts, telegram_service)
        self.feedback_service = feedback_service

    @show_typing
    def feedback_add(self, bot, update):
        text = update.message.text[len("/feedback"):].strip()
        if not text:
            update.message.reply_text(self.texts['missing-text'](update.effective_user.first_name))
            return
        self.feedback_service.add(update.effective_user.id, text)
        update.message.reply_text(self.texts['feedback-thanks'])
        if self.admin_id:
            bot.send_message(self.admin_id, self.texts['feedback-new'])

    @show_typing
    def admin_feedback_show(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        message = "\n".join([f"{feedback.id} / {feedback.created.date()} / {feedback.text}"
                             for feedback in self.feedback_service.get_all() if feedback.done is None])
        if message:
            update.message.reply_text(message)
        else:
            update.message.reply_text(self.texts['feedback-none'])

    @show_typing
    def admin_feedback_reply(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        text = update.message.text[len("/admin-feedback-reply"):].strip()
        parts = text.split(" ")
        if len(parts) < 2:
            update.message.reply_text(self.texts['feedback-include-id'])
            return
        feedback_id = parts[0]
        text = text[len(feedback_id):].strip()

        feedback = self.feedback_service.get(int(feedback_id))
        if not feedback:
            update.message.reply_text(self.texts['feedback-not-found'])
            return
        bot.send_message(feedback.user_id, f"{self.texts['feedback-reply-prefix']}\n{text}\n\n"
                                           f"{self.texts['feedback-reply-postfix']}")
        update.message.reply_text(self.texts['feedback-reply-sent'])

    @show_typing
    def admin_feedback_close(self, bot, update):
        if not self._is_admin(update.effective_user.id):
            return
        feedback_id = update.message.text[len("/admin-feedback-close"):].strip()
        if len(feedback_id) < 1:
            update.message.reply_text(self.texts['feedback-include-id'])
            return
        self.feedback_service.set_resolved(int(feedback_id))
        update.message.reply_text(self.texts['feedback-closed'])
