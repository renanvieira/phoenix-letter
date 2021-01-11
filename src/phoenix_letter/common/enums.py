from enum import IntEnum


class ReasonStopEnum(IntEnum):
    EMPTY_RECEIVED = (1,)
    MAX_MESSAGES_RECEIVED = 2
