import logging

from components.core import texts
from common.texts import bot_name
from components.announce.announce_command_handler import AnnounceCommandHandler
from components.announce.announce_component import AnnounceComponent
from components.core.core_command_handler import CoreCommandHandler
from components.core.core_component import CoreComponent
from components.core.texts import texts as core_texts
from components.user.texts import texts as user_texts
from components.feedback.texts import texts as feedback_texts
from components.announce.texts import texts as announce_texts
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
    core_command_handler = CoreCommandHandler(admin_id, core_texts, telegram_service)
    user_command_handler = UserCommandHandler(admin_id, user_texts, telegram_service, bot_name, user_service)
    feedback_service = FeedbackService()
    feedback_command_handler = FeedbackCommandHandler(admin_id, feedback_texts, telegram_service, feedback_service)
    announce_command_handler = AnnounceCommandHandler(admin_id, announce_texts, telegram_service, user_service)
    task_service = TaskService()
    doforme_command_handler = DoForMeCommandHandler(
        admin_id, doforme_texts, telegram_service, bot_name, task_service, user_service, feedback_service)
    components = {
        'core': CoreComponent(core_command_handler),
        'feedback': FeedbackComponent(feedback_command_handler),
        'user': UserComponent(user_command_handler),
        'announce': AnnounceComponent(announce_command_handler),
        'doforme': DoForMeComponent(doforme_command_handler),
    }
    bot = DoForMeBot(bot_name, texts.texts, components, admin_id, logger, user_service)
    return bot
