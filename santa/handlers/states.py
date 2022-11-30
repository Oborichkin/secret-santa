import enum


class State(enum.Enum):
    # COMMON
    IDLE = 0
    AWAIT_SANTA_ID = 1
    # MEMO
    MEMO = 2
    AWAIT_MEMO = 3
