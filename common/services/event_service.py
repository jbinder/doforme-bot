from logging import Logger

from common.common_event_type import CallbackStore
from common.event_type import EventType


class EventService:

    logger: Logger
    callbacks: CallbackStore

    def __init__(self, logger, callbacks: CallbackStore):
        self.callbacks = callbacks
        self.logger = logger

    def register_observer(self, event_type: EventType, observer: callable):
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(observer)

    def notify_observers(self, event_type: EventType, args: dict):
        if event_type not in self.callbacks:
            return
        for observer in self.callbacks[event_type]:
            observer(args)
