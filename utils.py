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


str_to_cmd = {
    '0': Commands.NO_OP,
    'X': Commands.NO_OP,
    '+': Commands.ACCELERATION,
    '-': Commands.DECELERATION,
    '<': Commands.CAR_INDEX_LEFT,
    '>': Commands.CAR_INDEX_RIGHT
}



class Directions(Enum):
    UP = '^'
    DOWN = 'v'
    RIGHT = '>'
    LEFT = '<'
    NONE = '-'


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
