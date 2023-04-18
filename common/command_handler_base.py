import abc

from common.services.event_service import EventService
from common.texts import texts as common_texts
from common.event_type import EventType
from common.services.telegram_service import TelegramService
from texts import texts as text_overrides


class CommandHandlerBase(metaclass=abc.ABCMeta):

    telegram_service: TelegramService
    event_service: EventService
    admin_id: int
    texts: dict

    def __init__(self, admin_id: int, event_service: EventService, texts: dict, telegram_service: TelegramService):
        self.admin_id = admin_id
        self.event_service = event_service
        self.texts = {**common_texts, **texts, **text_overrides}
        self.telegram_service = telegram_service

    def register_observer(self, event_type: EventType, observer: callable):
        self.event_service.register_observer(event_type, observer)

    def notify_observers(self, event_type: EventType, args: dict):
        self.event_service.notify_observers(event_type, args)

    def _is_admin(self, user_id):
        return self.admin_id and self.admin_id == user_id

    def _assure_private_chat(self, update):
        if not self.telegram_service.is_private_chat(update):
            update.message.reply_text(self.texts['private-chat-required'])
            return False
        return True
