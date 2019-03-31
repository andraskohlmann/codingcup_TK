from enum import Enum


def token():
    msg = {"token": "Xca2a9ZZM8k9IcXdR7UDRrYTdra3OxH7ud4PjbTlYqmXSkdb5PjaWQMQ0v0F5pYJl6SEH26zpFmHQ"}
    return msg


class Commands(Enum):
    NO_OP = "NO_OP"
    ACCELERATION = "ACCELERATION"
    DECELERATION = "DECELERATION"
    CAR_INDEX_LEFT = "CAR_INDEX_LEFT"
    CAR_INDEX_RIGHT = "CAR_INDEX_RIGHT"
    CLEAR = "CLEAR"
    FULL_THROTTLE = "FULL_THROTTLE"
    EMERGENCY_BRAKE = "EMERGENCY_BRAKE"
    GO_LEFT = "GO_LEFT"
    GO_RIGHT = "GO_RIGHT"


class Directions(Enum):
    UP = '^'
    DOWN = 'v'
    RIGHT = '>'
    LEFT = '<'


def command(game_id, tick, car_id, cmd: Commands):
    msg = {
      "response_id": {
        "game_id": game_id,
        "tick": tick,
        "car_id": car_id
      },
      "command": cmd.value
    }
    return msg
