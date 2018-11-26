import time
from datetime import datetime

from telegram.ext import CommandHandler

from common.services.telegram_service import TelegramService
from common.test.PtbTestCase import PtbTestCase
from components.doforme.tests.DfmMockbot import DfmMockbot
from components.doforme.texts import texts
from components.doforme.doforme_command_handler import DoForMeCommandHandler
from components.doforme.task_service import TaskService
from components.feedback.feedback_service import FeedbackService
from components.user.user_service import UserService


class TestDoForMeCommandHandler(PtbTestCase):

    def setUp(self):
        PtbTestCase.setUp(self)
        self._init_bot()
        from components.user.models import db
        db.drop_all_tables(with_all_data=True)
        db.create_tables()
        self.user_service = UserService()
        self.task_service = TaskService()
        self.admin_id = 42
        self.handler = DoForMeCommandHandler(self.admin_id, texts, TelegramService(self.user_service), "bot-name",
                                             self.task_service, self.user_service, FeedbackService())

    def _init_bot(self):
        dfm_bot = DfmMockbot()
        self.bot.getChat = dfm_bot.getChat
        self.bot.getChatMember = dfm_bot.getChatMember

    def test_job_weekly_review_activity_exists_should_sort_user_by_num_tasks_completed(self):
        self.updater.dispatcher.add_handler(CommandHandler("dummy_cmd", self.handler.job_weekly_review))
        self.updater.start_polling()
        update = self.mg.get_message(text=f"/dummy_cmd")
        user1_id = update.effective_user.id
        user2_id = update.effective_user.id + 1
        chat_id = update.effective_chat.id
        self.user_service.add_user_chat_if_not_exists(user2_id, chat_id)
        self.user_service.add_user_chat_if_not_exists(user1_id, chat_id)
        task1 = {'user_id': user1_id, 'chat_id': chat_id, 'owner_id': user2_id,
                 'title': 'task 1', 'due': datetime.utcnow()}
        self.task_service.add_task(task1)
        task = self.task_service.get_tasks(user1_id)[0]
        self.task_service.complete_task(task.id)

        self.bot.insertUpdate(update)
        time.sleep(2)  # the message takes some time to be sent...

        self.assertEqual(1, len(self.bot.sent_messages))
        sent = self.bot.sent_messages[0]
        # the message sent to the user
        self.assertEqual("sendMessage", sent['method'])
        lines = sent['text'].split("\n")
        for line in lines:
            if f"user {user2_id}:" in line:
                self.fail("Invalid user sort order.")
            if f"user {user1_id}:" in line:
                break
        self.updater.stop()
