from board import Board
from utils import command, Commands


class World:
    def __init__(self):
        self.game_id = None
        self.car_id = None
        self.tick = -1
        self.board = Board()

    def update(self, data: dict):
        if self.game_id is None:
            self.game_id = data['request_id']['game_id']
        if self.car_id is None:
            self.car_id = data['request_id']['car_id']

        if self.tick == data['request_id']['tick']:
            print("NO_OP SENT")
            return command(self.game_id, self.tick, self.car_id, Commands.NO_OP)

        self.tick = data['request_id']['tick']
        print(data)
        cmd = self.board.next_command(data)
        return command(self.game_id, self.tick, self.car_id, cmd)

    def next_command(self, data: dict) -> Commands:
        pass
