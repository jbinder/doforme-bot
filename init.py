from common.utils.logging_tools import get_logger
from components.announce.announce_command_handler import AnnounceCommandHandler
from components.announce.announce_component import AnnounceComponent
from components.core.core_command_handler import CoreCommandHandler
from components.core.core_component import CoreComponent
from components.core.job_log_service import JobLogService
from components.core.texts import texts as core_texts
from components.doforme.doforme_command_handler import DoForMeCommandHandler
from components.doforme.doforme_component import DoForMeComponent
from components.doforme.doforme_migration_handler import DoForMeMigrationHandler
from components.doforme.task_service import TaskService
from components.doforme.texts import texts as doforme_texts
from components.user.texts import texts as user_texts
from components.feedback.texts import texts as feedback_texts
from components.announce.texts import texts as announce_texts
from components.feedback.feedback_command_handler import FeedbackCommandHandler
from components.feedback.feedback_component import FeedbackComponent
from components.feedback.feedback_service import FeedbackService
from components.user.user_command_handler import UserCommandHandler
from components.user.user_component import UserComponent
from common.common_bot import CommonBot
from common.services.telegram_service import TelegramService
from components.user.user_migration_handler import UserMigrationHandler
from components.user.user_service import UserService
from texts import bot_name


def create_bot(admin_id: int):
    logger = get_logger()
    user_service = UserService()
    telegram_service = TelegramService(user_service, logger, [UserMigrationHandler(), DoForMeMigrationHandler()])
    core_command_handler = CoreCommandHandler(admin_id, core_texts, telegram_service)
    user_command_handler = UserCommandHandler(admin_id, user_texts, telegram_service, bot_name, user_service)
    feedback_service = FeedbackService()
    feedback_command_handler = FeedbackCommandHandler(admin_id, feedback_texts, telegram_service, feedback_service)
    announce_command_handler = AnnounceCommandHandler(admin_id, announce_texts, telegram_service, user_service)
    task_service = TaskService()
    job_log_service = JobLogService()
    doforme_command_handler = DoForMeCommandHandler(
        admin_id, doforme_texts, telegram_service, bot_name, task_service, user_service, feedback_service, 5,
        job_log_service)
    components = {
        'core': CoreComponent(core_command_handler),
        'feedback': FeedbackComponent(feedback_command_handler),
        'user': UserComponent(user_command_handler),
        'announce': AnnounceComponent(announce_command_handler),
        'doforme': DoForMeComponent(doforme_command_handler),
    }
    bot = CommonBot(components, logger)
    return bot
