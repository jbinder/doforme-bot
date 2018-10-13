import abc
from typing import Dict

import common
from common.event_type import EventType
from common.services.telegram_service import TelegramService


class CommandHandlerBase(metaclass=abc.ABCMeta):

    telegram_service: TelegramService
    callbacks: Dict[EventType, list]
    admin_id: int
    texts: dict

    def __init__(self, admin_id: int, texts: dict, telegram_service: TelegramService):
        self.telegram_service = telegram_service
        self.admin_id = admin_id
        self.texts = {**texts, **common.texts.texts}
        self.callbacks = {}

    def register_observer(self, event_type: EventType, observer: callable):
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(observer)

    def notify_observers(self, event_type: EventType, args: dict):
        for observer in self.callbacks[event_type]:
            observer(args)

    def _is_admin(self, user_id):
        return self.admin_id and self.admin_id == user_id

    def _assure_private_chat(self, update):
        if not self.telegram_service.is_private_chat(update):
            update.message.reply_text(self.texts['private-chat-required'])
            return False
        return True
