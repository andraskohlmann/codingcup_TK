import numpy as np

from utils import Commands, Directions


class Board:
    def __init__(self):
        default_map = def_map()
        self.default_map = np.array([[c for c in _] for _ in default_map])
        self.drivable_map = np.zeros_like(self.default_map)
        self.drivable_map[default_map == 'S'] = 1
        self.drivable_map[default_map == 'Z'] = 1

    def next_command(self, data: dict) -> Commands:
        passenger_location = data['passengers']['pos']
        stop_location = self.stop_location(passenger_location)
        dir_map = self.direction_map(stop_location)
        speed_map = self.speed_map(dir_map)
        command = self.strat(data, dir_map, speed_map)
        return command

    def stop_location(self, passenger_location):
        if self.drivable_map[passenger_location['y'] - 1, passenger_location['x']] == 1:
            return {'x': passenger_location['x'], 'y': passenger_location['y'] - 1}
        if self.drivable_map[passenger_location['y'], passenger_location['x'] - 1] == 1:
            return {'x': passenger_location['x'] - 1, 'y': passenger_location['y']}
        if self.drivable_map[passenger_location['y'], passenger_location['x'] + 1] == 1:
            return {'x': passenger_location['x'] + 1, 'y': passenger_location['y']}
        if self.drivable_map[passenger_location['y'] + 1, passenger_location['x']] == 1:
            return {'x': passenger_location['x'], 'y': passenger_location['y'] + 1}
        else:
            return None

    def direction_map(self, stop_location):
        direction_map = [[Directions.NONE for _ in row] for row in self.default_map]

        visited = np.zeros_like(self.drivable_map)
        visited[stop_location['y'], stop_location['x']] = 1
        iter = 1
        while iter in visited:
            indices = self.get_indices(visited, iter)
            for i in indices:
                self.set_visitors(visited, direction_map, i, iter + 1)
            iter += 1
        return direction_map

    def set_visitors(self, visited, direction_map, index, param):
        if self.drivable_map[index['y'] - 1, index['x']] == 1 and visited[index['y'] - 1, index['x']] == 1:
            visited[index['y'] - 1, index['x']] = param
            direction_map[index['y'] - 1, index['x']] = Directions.DOWN
        if self.drivable_map[index['y'], index['x'] - 1] == 1 and visited[index['y'], index['x'] - 1] == 1:
            visited[index['y'], index['x'] - 1] = param
            direction_map[index['y'], index['x'] - 1] = Directions.RIGHT
        if self.drivable_map[index['y'], index['x'] + 1] == 1 and visited[index['y'], index['x'] + 1] == 1:
            visited[index['y'], index['x'] + 1] = param
            direction_map[index['y'], index['x'] + 1] = Directions.LEFT
        if self.drivable_map[index['y'] + 1, index['x']] == 1 and visited[index['y'] + 1, index['x']] == 1:
            visited[index['y'] + 1, index['x']] = param
            direction_map[index['y'] + 1, index['x']] = Directions.UP

    def strat(self, data: dict, dir_map: np.array, speed_map: np.array) -> Commands:
        pass


    def speed_map(self, dir_map):
        return self.drivable_map

    def get_indices(self, visited, iter):
        indices = []
        for i, row in enumerate(visited):
            for j, col in enumerate(row):
                if col == iter:
                    indices.append({'x': j, 'y': i})
        return indices


def def_map():
    return np.array([
        'GPSSPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGPSSPG',
        'PPSSPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPSSPP',
        'SSSSSSSSSSSSSSSSSSSSSSSSSSSSZSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSS',
        'SSSSSSSSSSSSSSSSSSSSSSSSSSSSZSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSS',
        'PPSSPPPZZPPPPPPPPPPPPPPPPPPPPSSPPPPPPPPPPPPPPPPPPPPZZPPPSSPP',
        'GPSSPGPSSPGBBGBBGGBBGGBBGBBGPSSPGBBGBBGGBBGGBBGBBGPSSPBPSSPG',
        'GPSSPBPSSPPPPPPPPPPPPPPPPPPPPSSPPPPPPPPPPPPPPPPPPPPSSPBPSSPG',
        'GPSSPBPSSSSSSSSZSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSPGPSSPG',
        'GPSSPBPSSSSSSSSZSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSPBPSSPG',
        'GPSSPBPSSPPPPPPPSSPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPSSPBPSSPG',
        'GPSSPGPSSSPPGBBPSSPGGGGGBBBBBGPPPPPPPPGGBBBBBBGBBPSSSPGPSSPG',
        'GPSSPBPSSSSPPGBPSSPGTGPPPPPPPPPSSSSSSPPPBBBBBBGBBPSGSPBPSSPG',
        'GPSSPBPPSSSSPPGPSSPGGGPSSSSSSSSSSSSSSSSPPPGGGPPPPPSGSPBPSSPG',
        'GPSSPGGPPSSSSPPPSSPPBBPSSSSSSSSSSPPSSSSSSPPPGPSSSSSGSPGPSSPG',
        'GPSSPGGGPPSSSSPSSSSPPPPSSPSSPPSSPPPPPSSSSSSPPPSSSSSSSPGPSSPG',
        'GPSSPGGGGPPSSSSSBBSSSSSSSSSSPPSSSSSSPPPSSSSSSZSSPPPPPPGPSSPG',
        'GPSSPGGGGGPPSSSSBBSSSSSSSSSSPPSPPPPSSSPPPSSSSZSSPPSSPGGPSSPG',
        'GPSSPGGGGGGPPPPSSSSPPPPPPPPPPPSPPSSSSSSPPPPPPPSSPPSSPTTPSSPG',
        'GPSSPGGGGGGGGGPPSSPPSSSSSSSSGPSSSSPPSSSSPPGTGPSSSSSSPTGPSSPG',
        'GPSSPGGGGGGBBBGPSSSSSSSSSSSSSPPPPPPPPSSSSPPGPPSSSSSSPTTPSSPG',
        'GPSSPGGGGGGBBBGPSSSSSSPPPPSSSSSSSSSSPPSSSSPPPSSSPPPPPTTPSSPG',
        'GPSSPGGGGGGBBBGPSSPPPPPGGPPSSSSSSSSSSPPSSSSPSSSSPBBBBTGPSSPG',
        'GPSSPGPPPPPPPPPPSSPGGGGGGGPPPPPPPPSSSSPPSSSSSSSPPBBBBBGPSSPG',
        'GPSSPGPSSSSSSSSSSSPGGGGGGGGGGGBBGPPSSSSPPSSSSSPPGGGGGGGPSSPG',
        'GPSSPGPSSSSSSSSSSSPGGGGBGGGGGGBBGGPPSSSSPPPPSSSPPPPPPGTPSSPG',
        'GPSSPGPSSPPPPPPPSSPGGGGGGGGGGGGGGGGPPSSSSSSPSSSSSSSSPGTPSSPG',
        'GPSSPGPSSPBGBBBPSSPGGGGGGGGGGPPPPGGGPPSSSSSPPSSSSSSSPGTPSSPG',
        'GPSSPGPSSPBGBBBPSSPGGGGGGGGGPPSSPPGGGPPPPPPPPPPPPPZZPPGPSSPG',
        'GPZZPPPZZPPPPPPPSSPPPPPPPPPPPSSSSPPPPPPPPPPPPPPPPSSSSPPPZZPG',
        'GPSSSSSSSSSSSSSSSSSSSSSSSSSSSSBBSSSSSSSSSSSSSSSSSSBBSSSSSSPG',
        'GPSSSSSSSSSSSSSSSSSSSSSSSSSSSSBBSSSSSSSSSSSSSSSSSSBBSSSSSSPG',
        'GPZZPPPPPPPPPPPPPPPPSSPPPPPPPSSSSPPPPPPPSSPPPPPPPSSSSPPPZZPG',
        'GPSSPGPSSSSPPBBBBPPSSSPGGPPPPPSSPPPPPGGPSSSPPGBBPPSSPPGPSSPG',
        'GPSSPBPSSSSSPBBBBPSSSSPBBPSSSSSSSSSSPGGPSSSSPGBBGPSSPGBPSSPG',
        'GPSSPBPPPSSSPGGGGPSSSPPGGPSSSSSSSSSSPGGPPSSSPGGGGPSSPGBPSSPG',
        'GPSSPGGGPPSSPGGGGPSSPPGGGPSSPPPPPPSSPGGGPPSSPGGGGPSSPGBPSSPG',
        'GPSSPGGBBPSSPGGGGPSSPGGGBPSSPGGGGPSSPGGGGPSSPGGGGPSSPGBPSSPG',
        'GPSSPGGBBPSSPGGGGPSSPGBBBPSSPGGGGPSSPGGGGPSSPGGGGPSSPGBPSSPG',
        'GPSSPGPPPPSSPPPPPPZZPPPPPPZZPPPPPPSSPPPPPPZZPPPPPPZZPPGPSSPG',
        'GPSSPBPSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSZSSZSSSSSSSSPBPSSPG',
        'GPSSPBPSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSZSSZSSSSSSSSPBPSSPG',
        'GPSSPGPSSPPPPPSSPPPPPPPPPPPPZZPPPPPZZPPPPPSSPPPPPSSPPPBPSSPG',
        'GPSSPBPSSPGGGPSSPGGGGGGGBBBPSSPGGGPSSPBBGPSSPGBBPSSPBGBPSSPG',
        'GPSSPBPSSPGGGPSSPGGGGGGGBBBPSSPGGGPSSPBBGPSSPGBBPSSPBGBPSSPG',
        'GPSSPGPSSPPPPPZZPPPPPPPPPPPPSSPPPPPSSPPPPPSSPPPPPSSPPGGPSSPG',
        'GPSSPGPSSSSSSZSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSPGBPSSPG',
        'GPSSPGPSSSSSSZSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSPGBPSSPG',
        'GPSSPGPPSSPPPPZZPPPPSSPPPPZZPPPPSSPPPPPPPPPPSSPPPPZZPGBPSSPG',
        'GPSSPGGPSSPBBPSSPBBPSSPGBPSSPBGPSSPGGGGGGGGPSSPGGPSSPGBPSSPG',
        'GPSSPGGPSSPBBPSSPBBPSSPBBPSSPBGPSSPGGGGGGGGPSSPGGPSSPGBPSSPG',
        'GPSSPGGPSSPPPPSSPPPPZZPPPPSSPPPPZZPPPPPPPPPPZZPPPPSSPGGPSSPG',
        'GPSSPGGPSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSPPPGGPSSPG',
        'GPSSPGGPSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSPGGGGPSSPG',
        'GPSSPGGPPPPPPPPPPPPPPPPPPPPPPSSPPPPPPPPPPPPPPPPPPPPGGGGPSSPG',
        'GPSSPGGGGGGGGGGGGGBBBBGGBBBBPSSPBBBBGGBBBBGGGGGGGGGGGGGPSSPG',
        'PPSSPPPPPPPPPPPPPPPPPPPPPPPPPSSPPPPPPPPPPPPPPPPPPPPPPPPPSSPP',
        'SSSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSZSSSS',
        'SSSSZSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSZSSSS',
        'PPSSPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPSSPP',
        'GPSSPGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGPSSPG'
    ])
