from enum import Enum


class UserState(Enum):
    SETUP = "setup"
    WAITING = "waiting"
    CHATTING = "chatting"
    IDLE = "idle"


class SetupState(Enum):
    AGE = "age"
    GENDER = "gender"
    ROOM = "room"
    COMPLETE = "complete"
