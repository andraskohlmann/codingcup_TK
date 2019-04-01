import numpy as np

from utils import Commands, Directions, str_to_cmd


def turn_dir(direction, desired_direction):
    if desired_direction == Directions.UP:
        if direction == Directions.RIGHT:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT
    elif  desired_direction == Directions.RIGHT:
        if direction == Directions.DOWN:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT
    elif  desired_direction == Directions.LEFT:
        if direction == Directions.UP:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT
    else:
        if direction == Directions.LEFT:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT


def look_ahead(lookup_map, pos, direction, speed):
    if direction == Directions.UP:
        v_x = 0
        v_y = -speed
    elif direction == Directions.DOWN:
        v_x = 0
        v_y = speed
    elif direction == Directions.LEFT:
        v_x = -speed
        v_y = 0
    elif direction == Directions.RIGHT:
        v_x = speed
        v_y = 0
    return lookup_map[(pos['y'] + v_y) % 60, (pos['x'] + v_x) % 60]


class Board:
    def __init__(self):
        default_map = def_map()
        self.default_map = np.array([[c for c in _] for _ in default_map])
        self.drivable_map = np.zeros_like(self.default_map, dtype=int)
        self.drivable_map[self.default_map == 'S'] = 1
        self.drivable_map[self.default_map == 'Z'] = 1

        self.size_y, self.size_x = self.drivable_map.shape

    def next_command(self, data: dict) -> Commands:
        if 'passenger_id' in data['cars'][0]:
            passenger_location = [_ for _ in data['passengers'] if _['id'] == data['cars'][0]['passenger_id']][0]['dest_pos']
        else:
            passenger_location = data['passengers'][0]['pos']
        stop_location = self.stop_location(passenger_location)
        dir_map = self.direction_map(stop_location)
        speed_map = self.speed_map(dir_map, stop_location)
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
        direction_map = np.array([[Directions.NONE for _ in row] for row in self.default_map])

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
        if self.drivable_map[(index['y'] - 1) % self.size_y, (index['x']) % self.size_x] == 1 and visited[(index['y'] - 1) % self.size_y, (index['x']) % self.size_x] < 1:
            visited[(index['y'] - 1) % self.size_y, (index['x']) % self.size_x] = param
            direction_map[(index['y'] - 1) % self.size_y, (index['x']) % self.size_x] = Directions.DOWN
        if self.drivable_map[(index['y']) % self.size_y, (index['x'] - 1) % self.size_x] == 1 and visited[(index['y']) % self.size_y, (index['x'] - 1) % self.size_x] < 1:
            visited[(index['y']) % self.size_y, (index['x'] - 1) % self.size_x] = param
            direction_map[(index['y']) % self.size_y, (index['x'] - 1) % self.size_x] = Directions.RIGHT
        if self.drivable_map[(index['y']) % self.size_y, (index['x'] + 1) % self.size_x] == 1 and visited[(index['y']) % self.size_y, (index['x'] + 1) % self.size_x] < 1:
            visited[(index['y']) % self.size_y, (index['x'] + 1) % self.size_x] = param
            direction_map[(index['y']) % self.size_y, (index['x'] + 1) % self.size_x] = Directions.LEFT
        if self.drivable_map[(index['y'] + 1) % self.size_y, (index['x']) % self.size_x] == 1 and visited[(index['y'] + 1) % self.size_y, (index['x']) % self.size_x] < 1:
            visited[(index['y'] + 1) % self.size_y, (index['x']) % self.size_x] = param
            direction_map[(index['y'] + 1) % self.size_y, (index['x']) % self.size_x] = Directions.UP

    def strat(self, data: dict, dir_map: np.array, speed_map: np.array) -> Commands:
        car = [_ for _ in data['cars'] if _['id'] == 0][0]
        pos = car['pos']
        speed = car['speed']
        direction = Directions[car['direction']]
        command = Commands.NO_OP
        prev_command = Commands.NO_OP
        if 'command' in car:
            if car['command'] == 'X':
                return Commands.NO_OP
            prev_command = str_to_cmd[car['command']]
        if direction != dir_map[pos['y'], pos['x']] and speed > 0\
                and prev_command != Commands.CAR_INDEX_RIGHT\
                and prev_command != Commands.CAR_INDEX_LEFT:
            return Commands.EMERGENCY_BRAKE
        desired_dir = look_ahead(dir_map, pos, direction, speed)
        desired_speed = look_ahead(speed_map, pos, direction, speed)

        if desired_dir == Directions.NONE:
            print('NONE as desired')
            return Commands.EMERGENCY_BRAKE

        print("Dir: {}, desired {}".format(direction, desired_dir))
        print("Speed: {}, desired {}".format(speed, desired_speed))

        if desired_speed < speed and desired_dir == direction:
            if prev_command != Commands.DECELERATION:
                return Commands.DECELERATION
            else:
                return Commands.NO_OP
        if desired_speed > speed and desired_dir == direction:
            if prev_command != Commands.ACCELERATION:
                return Commands.ACCELERATION
            else:
                return Commands.NO_OP
        if desired_dir != direction:
            if speed == 0 and prev_command != Commands.CAR_INDEX_LEFT and prev_command != Commands.CAR_INDEX_RIGHT:
                print(command)
                return turn_dir(direction, desired_dir)
            else:
                if prev_command != Commands.CAR_INDEX_LEFT and prev_command != Commands.CAR_INDEX_RIGHT:
                    return turn_dir(direction, desired_dir)
        return command

    def speed_map(self, dir_map, stop_pos):
        # TODO: optmize and manage borders

        left_map = self.speed_map_in_dir(dir_map, Directions.LEFT)
        right_map = self.speed_map_in_dir(dir_map, Directions.RIGHT)
        up_map = self.speed_map_in_dir(dir_map, Directions.UP)
        down_map = self.speed_map_in_dir(dir_map, Directions.DOWN)
        speed_map = left_map + right_map + up_map + down_map

        # print(dir_map)
        # print(speed_map)
        speed_map = self.drivable_map.copy()
        speed_map[stop_pos['y'], stop_pos['x']] = 0
        return speed_map

    def speed_map_in_dir(self, dir_map, direction):
        dir_speed_map = np.zeros_like(self.drivable_map)
        max_speed = 1

        for i in range(60):
            for j in range(60):
                x, y = self.transform_coord(direction, i, j)
                if dir_map[x, y] == direction:
                    dir_speed_map[x, y] = max_speed
                    max_speed = max_speed + 1 if max_speed < 3 else 3
                else:
                    max_speed = 1
            max_speed = 1

        return dir_speed_map

    def transform_coord(self, direction, x, y):
        if direction == Directions.LEFT:
            return x, y
        if direction == Directions.RIGHT:
            return x, 59 - y
        if direction == Directions.UP:
            return y, x
        if direction == Directions.DOWN:
            return 59 - y, x

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
