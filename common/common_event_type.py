from typing import Dict

from common.event_type import EventType


class CommonEventType(EventType):
    USER_SEND_FAILED = 1
    CHAT_SEND_FAILED = 2


CallbackStore = Dict[EventType, list[object]]
