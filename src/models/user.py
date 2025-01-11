from dataclasses import dataclass
from src.models.states import SetupState


@dataclass
class UserSettings:
    age: int = 0
    gender: str = ""
    room: str = "general"
    setup_state: SetupState = SetupState.AGE

    def to_dict(self):
        return {
            "age": self.age,
            "gender": self.gender,
            "room": self.room,
        }
