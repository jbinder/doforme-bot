import logging

import texts
from common.texts import bot_name
from components.user.texts import texts as user_texts
from components.feedback.texts import texts as feedback_texts
from components.doforme.texts import texts as doforme_texts
from components.doforme.doforme_command_handler import DoForMeCommandHandler
from components.doforme.doforme_component import DoForMeComponent
from components.feedback.feedback_command_handler import FeedbackCommandHandler
from components.feedback.feedback_component import FeedbackComponent
from components.feedback.feedback_service import FeedbackService
from components.user.user_command_handler import UserCommandHandler
from components.user.user_component import UserComponent
from do_for_me_bot import DoForMeBot
from components.doforme.task_service import TaskService
from common.services.telegram_service import TelegramService
from components.user.user_service import UserService


def get_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    return logging.getLogger(__name__)


def create_bot(admin_id: int):
    logger = get_logger()
    user_service = UserService()
    telegram_service = TelegramService(user_service)
    user_command_handler = UserCommandHandler(admin_id, user_texts, telegram_service, bot_name, user_service)
    feedback_service = FeedbackService()
    feedback_command_handler = FeedbackCommandHandler(admin_id, feedback_texts, telegram_service, feedback_service)
    task_service = TaskService()
    doforme_command_handler = DoForMeCommandHandler(
        admin_id, doforme_texts, telegram_service, bot_name, task_service, user_service, feedback_service)
    components = {
        'feedback': FeedbackComponent(feedback_command_handler),
        'user': UserComponent(user_command_handler),
        'doforme': DoForMeComponent(doforme_command_handler),
    }
    bot = DoForMeBot(bot_name, texts.texts, components, admin_id, logger, user_service)
    return bot
