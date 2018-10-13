import abc
from typing import Dict

from common.event_type import EventType


class CommandHandlerBase(metaclass=abc.ABCMeta):

    callbacks: Dict[EventType, list]
    admin_id: int
    texts: dict

    def __init__(self, admin_id, texts):
        self.admin_id = admin_id
        self.texts = texts
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
