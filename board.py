import numpy as np

from utils import Commands, Directions, str_to_cmd, c
from visual import save_dir_map, save_poss_dir_map


def turn_dir(direction, desired_direction):
    if desired_direction == Directions.UP:
        if direction == Directions.RIGHT:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT
    elif desired_direction == Directions.RIGHT:
        if direction == Directions.DOWN:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT
    elif desired_direction == Directions.LEFT:
        if direction == Directions.UP:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT
    else:
        if direction == Directions.LEFT:
            return Commands.CAR_INDEX_LEFT
        else:
            return Commands.CAR_INDEX_RIGHT


def resulting_dir(direction, prev_command):
    if direction == Directions.UP:
        if prev_command == Commands.CAR_INDEX_RIGHT:
            return Directions.RIGHT
        else:
            return Directions.LEFT
    elif direction == Directions.RIGHT:
        if prev_command == Commands.CAR_INDEX_RIGHT:
            return Directions.DOWN
        else:
            return Directions.UP
    elif direction == Directions.LEFT:
        if prev_command == Commands.CAR_INDEX_RIGHT:
            return Directions.UP
        else:
            return Directions.DOWN
    else:
        if prev_command == Commands.CAR_INDEX_RIGHT:
            return Directions.LEFT
        else:
            return Directions.RIGHT


def look_ahead(pos, direction, speed, prev_command):
    v_x = 0
    v_y = 0

    if direction == Directions.UP:
        v_y = -speed
    elif direction == Directions.DOWN:
        v_y = speed
    elif direction == Directions.LEFT:
        v_x = -speed
    elif direction == Directions.RIGHT:
        v_x = speed

    new_pos = {'x': (pos['x'] + v_x) % 60, 'y': (pos['y'] + v_y) % 60}

    new_speed = speed
    if prev_command == Commands.DECELERATION:
        new_speed = max(0, speed - 1)
    elif prev_command == Commands.ACCELERATION:
        new_speed = min(speed + 1, 3)

    new_dir = direction
    if prev_command == Commands.CAR_INDEX_LEFT or prev_command == Commands.CAR_INDEX_RIGHT:
        new_dir = resulting_dir(direction, prev_command)

    return new_pos, new_dir, new_speed


def look_way_ahead(pos, direction, speed=1):
    v_x = 0
    v_y = 0

    if direction == Directions.UP:
        v_y = -speed
    elif direction == Directions.DOWN:
        v_y = speed
    elif direction == Directions.LEFT:
        v_x = -speed
    elif direction == Directions.RIGHT:
        v_x = speed

    new_pos = {'x': (pos['x'] + v_x) % 60, 'y': (pos['y'] + v_y) % 60}

    return new_pos


def opposite_dir(direction):
    return resulting_dir(
        resulting_dir(
            direction, Commands.CAR_INDEX_LEFT
        ), Commands.CAR_INDEX_LEFT
    )


class Board:
    def __init__(self):
        default_map = def_map()
        self.default_map = np.array([[c for c in _] for _ in default_map])
        self.drivable_map = np.zeros_like(self.default_map, dtype=int)
        self.drivable_map[self.default_map == 'S'] = 1
        self.drivable_map[self.default_map == 'Z'] = 1

        self.size_y, self.size_x = self.drivable_map.shape

        self.possible_directions = self.set_possible_directions()
        # save_poss_dir_map(self.possible_directions)

    def next_command(self, data: dict) -> Commands:
        our_car = [c for c in data['cars'] if c['id'] == data['request_id']['car_id']][0]
        if 'passenger_id' in our_car:
            passenger_location = [_ for _ in data['passengers'] if _['id'] == our_car['passenger_id']][0]['dest_pos']
        else:
            passenger_location = self.find_closest_passenger(data['passengers'], our_car['pos'])
        stop_location = self.stop_location(passenger_location)
        drivable_map_with_cars = self.drivable_map_with_obsticles(data['cars'], data['pedestrians'], data['request_id']['car_id'])
        dir_map, visited = self.direction_map(drivable_map_with_cars, stop_location)
        # save_dir_map(dir_map, data['request_id']['tick'])
        # if dir_map[our_car['pos']['y'], our_car['pos']['x']] == Directions.NONE \
        #         and self.default_map[our_car['pos']['y'], our_car['pos']['x']] == 'S':
        #     print(visited)
        speed_map = self.speed_map(dir_map, stop_location)
        command = self.strat(data, dir_map, speed_map, drivable_map_with_cars)
        return command

    def stop_location(self, passenger_location):
        # Normal case, stop location is next to the road
        for nb_dir in [Directions.DOWN, Directions.UP, Directions.RIGHT, Directions.LEFT]:
            nb_pos = look_way_ahead(passenger_location, nb_dir)
            if self.drivable_map[nb_pos['y'], nb_pos['x']] == 1:
                return nb_pos
        # Special case, need to extend the drivable area
        for nb_dir in [Directions.DOWN, Directions.UP, Directions.RIGHT, Directions.LEFT]:
            nb_pos = look_way_ahead(passenger_location, nb_dir)
            if self.default_map[nb_pos['y'], nb_pos['x']] == 'P':
                self.default_map[nb_pos['y'], nb_pos['x']] = 'S'
                self.drivable_map[nb_pos['y'], nb_pos['x']] = 1
                for nb_nb_dir in [Directions.DOWN, Directions.UP, Directions.RIGHT, Directions.LEFT]:
                    nb_nb_pos = look_way_ahead(nb_pos, nb_nb_dir)
                    if self.default_map[nb_nb_pos['y'], nb_nb_pos['x']] == 'S':
                        self.add_posible_direction(nb_nb_pos, opposite_dir(nb_nb_dir))
                        self.add_posible_direction(nb_pos, nb_nb_dir)
                return nb_pos
        return None

    def direction_map(self, drivable_map_with_cars, stop_location):
        direction_map = np.array([[Directions.NONE for _ in row] for row in self.default_map])
        visited = np.zeros_like(drivable_map_with_cars)
        visited[stop_location['y'], stop_location['x']] = 1
        iter = 1
        while iter in visited:
            indices = self.get_indices(visited, iter)
            for i in indices:
                self.set_visitors(drivable_map_with_cars, visited, direction_map, i, iter + 1)
            iter += 1
        return direction_map, visited

    def set_visitors(self, drivable_map_with_cars, visited, direction_map, index, param):
        for visit_dir in [Directions.DOWN, Directions.UP, Directions.RIGHT, Directions.LEFT]:
            next_pos = look_way_ahead(index, visit_dir)
            if drivable_map_with_cars[next_pos['y'], next_pos['x']] == 1 \
                    and visited[next_pos['y'], next_pos['x']] < 1:
                desired_dir = opposite_dir(visit_dir)
                if desired_dir in self.possible_directions[next_pos['y'], next_pos['x']]:
                    visited[next_pos['y'], next_pos['x']] = param
                    direction_map[next_pos['y'], next_pos['x']] = desired_dir

    def strat(self, data: dict, dir_map: np.array, speed_map: np.array, drivable_map_with_cars: np.array) -> Commands:
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

        new_pos, new_dir, new_speed = look_ahead(pos, direction, speed, prev_command)
        newest_pos = look_way_ahead(new_pos, new_dir, new_speed)

        desired_dir = dir_map[newest_pos['y'], newest_pos['x']]
        desired_speed = speed_map[newest_pos['y'], newest_pos['x']]

        print("Pos: {}, new pos {}, newest {}".format(pos, new_pos, newest_pos))
        print("Dir: {}, new dir {}, desired {}".format(direction, new_dir, desired_dir))
        print("Speed: {}, desired {}".format(speed, desired_speed))
        print("Life: {}, tick: {}, transp: {}".format(
            data['cars'][0]['life'],
            data['request_id']['tick'],
            data['cars'][0]['transported'])
        )

        if desired_speed == 0 or (
            new_speed == 1 and new_pos == pos and desired_dir != new_dir
        ) or (
            not drivable_map_with_cars[newest_pos['y'], newest_pos['x']]
        ) or (
            dir_map[new_pos['y'], new_pos['x']] == opposite_dir(direction) and speed > 0
        ) or (
            dir_map[new_pos['y'], new_pos['x']] == opposite_dir(new_dir) and speed > 0
        ):
            command = Commands.DECELERATION
        else:
            if desired_dir == new_dir:
                if speed == 0 and prev_command != Commands.ACCELERATION:
                    command = Commands.ACCELERATION
                else:
                    command = Commands.NO_OP
            else:
                command = turn_dir(new_dir, desired_dir)

        # if self.default_map[newest_pos['y'], newest_pos['x']] in ['P', 'B']:
        #     command = Commands.EMERGENCY_BRAKE

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
        # speed_map = self.drivable_map.copy()
        speed_map[stop_pos['y'], stop_pos['x']] = 0
        return speed_map

    def speed_map_in_dir(self, dir_map, direction):
        dir_speed_map = np.zeros_like(self.drivable_map)
        max_speed = 1

        for i in range(60):
            left = 0
            right = 0
            while left < 59 and right < 59:
                x, y = self.transform_coord(direction, i, right)
                while right < 59 and dir_map[x, y] == direction:
                    right += 1
                    x, y = self.transform_coord(direction, i, right)
                # print(direction, left, right, x, y)
                counter = 0
                for idx in range(right - 1, left - 1, -1):
                    if counter < 2:
                        dir_speed_map[x, idx] = 1
                    elif counter < 5:
                        dir_speed_map[x, idx] = 2
                    else:
                        dir_speed_map[x, idx] = 3
                    counter += 1

                left = right + 1
                right = left
            #
            # for j in range(60):
            #     x, y = self.transform_coord(direction, i, j)
            #     if dir_map[x, y] == direction:
            #         dir_speed_map[x, y] = max_speed
            #         max_speed = max_speed + 1 if max_speed < 3 else 3
            #     else:
            #         max_speed = 1
            # max_speed = 1

        return dir_speed_map

    @staticmethod
    def transform_coord(direction, x, y):
        if direction == Directions.LEFT:
            return x, y
        if direction == Directions.RIGHT:
            return x, 59 - y
        if direction == Directions.UP:
            return y, x
        if direction == Directions.DOWN:
            return 59 - y, x

    @staticmethod
    def get_indices(visited, iter):
        indices = []
        for i, row in enumerate(visited):
            for j, col in enumerate(row):
                if col == iter:
                    indices.append({'x': j, 'y': i})
        return indices

    def set_possible_directions(self):
        go = True
        circulated = np.array([[False for _ in row] for row in self.default_map])
        possible_dirs = np.array([[[Directions.NONE] * 4 for _ in row] for row in self.default_map])
        while go:
            candidate, start_dir = self.get_unvisited_road(circulated)
            if candidate is None:
                go = False
            else:
                self.circulate(candidate, start_dir, circulated, possible_dirs)
        return possible_dirs

    def get_unvisited_road(self, circulated):
        for y in range(len(self.default_map)):
            for x in range(len(self.default_map[y])):
                if self.default_map[y, x] == 'S' and not circulated[y, x]:
                    if self.default_map[c(y + 1), c(x)] in ['P', 'G'] \
                            and self.default_map[c(y - 1), c(x)] == 'S' \
                            and self.default_map[c(y - 2), c(x)] in ['P', 'G']:
                        return {'x': x, 'y': y}, Directions.RIGHT
                    elif self.default_map[c(y - 1), c(x)] in ['P', 'G'] \
                            and self.default_map[c(y + 1), c(x)] == 'S' \
                            and self.default_map[c(y + 2), c(x)] in ['P', 'G']:
                        return {'x': x, 'y': y}, Directions.LEFT
                    elif self.default_map[c(y), c(x + 1)] in ['P', 'G'] \
                            and self.default_map[c(y), c(x - 1)] == 'S' \
                            and self.default_map[c(y), c(x - 2)] in ['P', 'G']:
                        return {'x': x, 'y': y}, Directions.UP
                    elif self.default_map[c(y), c(x - 1)] in ['P', 'G'] \
                            and self.default_map[c(y), c(x + 1)] == 'S' \
                            and self.default_map[c(y), c(x + 2)] in ['P', 'G']:
                        return {'x': x, 'y': y}, Directions.DOWN
        return None, None

    def circulate(self, candidate, start_dir, circulated, possible_dirs):
        right_nb = look_way_ahead(candidate, resulting_dir(start_dir, Commands.CAR_INDEX_RIGHT))
        front_nb = look_way_ahead(candidate, start_dir)
        if self.default_map[right_nb['y'], right_nb['x']] not in ['P', 'G']:
            main_dir = resulting_dir(start_dir, Commands.CAR_INDEX_RIGHT)
        elif self.default_map[front_nb['y'], front_nb['x']] in ['P', 'G']:
            main_dir = resulting_dir(start_dir, Commands.CAR_INDEX_LEFT)
        else:
            main_dir = start_dir
        circulated[candidate['y'], candidate['x']] = True
        possible_dirs[candidate['y'], candidate['x']] = [
            main_dir, resulting_dir(main_dir, Commands.CAR_INDEX_LEFT), Directions.NONE, Directions.NONE
        ]
        next_candidate = look_way_ahead(candidate, main_dir)
        if not circulated[next_candidate['y'], next_candidate['x']]:
            self.circulate(next_candidate, main_dir, circulated, possible_dirs)

    def add_posible_direction(self, position, direction):
        for i in range(4):
            if self.possible_directions[position['y'], position['x'], i] == Directions.NONE:
                self.possible_directions[position['y'], position['x'], i] = direction
                break

    def drivable_map_with_obsticles(self, cars, peds, car_id):
        drivable_map_with_obsticles = np.copy(self.drivable_map)
        for car in cars:
            if car['id'] is not car_id:
                future_car_pos, future_car_dir, future_car_speed = look_ahead(car['pos'], Directions[car['direction']],
                                                                              car['speed'], str_to_cmd[car['command']])
                very_future_car_pos = look_way_ahead(future_car_pos, future_car_dir, future_car_speed)
                positions = self.get_positions_between(future_car_pos, very_future_car_pos)
                for pos in positions:
                    drivable_map_with_obsticles[pos['y']][pos['x']] = 0
        for ped in peds:
            future_ped_pos, future_ped_dir, future_ped_speed = look_ahead(ped['pos'], Directions[ped['direction']],
                                                                          ped['speed'], str_to_cmd[ped['command']])
            very_future_ped_pos = look_way_ahead(future_ped_pos, future_ped_dir, future_ped_speed)
            positions = self.get_positions_between(future_ped_pos, very_future_ped_pos)
            for pos in positions:
                drivable_map_with_obsticles[pos['y']][pos['x']] = 0
        return drivable_map_with_obsticles

    @staticmethod
    def get_positions_between(pos, new_pos):
        if pos == new_pos:
            return [pos]

        positions = [pos]
        if pos['x'] == new_pos['x']:
            ys = range(new_pos['y'], pos['y'], 1 if new_pos['y'] < pos['y'] else -1)
            for y in ys:
                positions.append({'x': pos['x'], 'y': y})
        else:
            xs = range(new_pos['x'], pos['x'], 1 if new_pos['x'] < pos['x'] else -1)
            for x in xs:
                positions.append({'x': x, 'y': pos['y']})
        return positions

    @staticmethod
    def find_closest_passenger(passengers, our_pos):
        min_dist = 120
        pos = None
        for passenger in passengers:
            dist_x = abs(passenger['pos']['x'] - our_pos['x'])
            dist_x = min(dist_x, 60 - dist_x)
            dist_y = abs(passenger['pos']['y'] - our_pos['y'])
            dist_y = min(dist_y, 60 - dist_y)
            man_dist = dist_x + dist_y
            if man_dist < min_dist:
                min_dist = man_dist
                pos = passenger['pos']
        return pos

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
