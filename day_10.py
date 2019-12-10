# AOC day 9

import logging
import sys

import numpy as np
import math

class MonitoringStation(object):

    def __init__(self):

        self.map = []
        self.asteroids = []
        self.cols = 0
        self.rows = 0
        self.best_station = ()

    def load_file(self, file_name):

        with open(file_name, 'r') as f:
            map_lines = f.readlines()
            self.load_map(map_lines)
    
    def load_map(self, map_lines):

        self.asteroids = []
        self.cols = 0
        self.rows = 0
        self.best_station = ()

        self.rows = len(map_lines)
        for (y, line) in enumerate(map_lines):
            line = line.strip()
            
            if self.cols == 0:
                self.cols = len(line)
            assert len(line) == self.cols

            for (x, char) in enumerate(line):
                if char == '#':
                    self.asteroids.append((x, y))

        self.map = np.zeros((self.rows, self.cols), dtype=int)
        for (x, y) in self.asteroids:
            self.map[y, x] = 1

        self.print_map()

    def print_map(self):

        logging.debug("Map has {} rows and {} columns".format(self.rows, self.cols))
        logging.debug("Map content:\n {}".format(self.map))

    def find_best_position(self):

        best_row = 0
        best_col = 0
        num_seen = 0

        asteroids_visible = np.zeros((self.rows, self.cols), dtype=int)

        # Loop over all asteroids as possible stations
        for (s_x, s_y) in self.asteroids:
            visible_angles = set()

            # Loop over all asteroids, skipping if candidate station
            for (a_x, a_y) in self.asteroids:
                if (a_x, a_y) == (s_x, s_y):
                    continue 

                # Calculate angle from station to current asteroid
                a_angle = math.atan2((a_y - s_y), (a_x - s_x))

                # If the angle is new, add to set
                if a_angle not in visible_angles:
                    visible_angles.add(a_angle)
            
            asteroids_visible[s_y, s_x] = len(visible_angles)

        logging.debug("\n {}".format(asteroids_visible))
        
        best_y, best_x = np.unravel_index(asteroids_visible.argmax(), asteroids_visible.shape)
        self.best_station = (best_x, best_y)
        num_seen = asteroids_visible[best_y, best_x]

        return (best_x, best_y, num_seen)

    def vaporize(self, station, nth_vaporized):

        def angle(x,y):

            return round((math.atan2(x,y) + 2*math.pi) %(2*math.pi), 10)

        def mag(dx, dy):

            return (dx**2 + dy**2)

        vecs = {}

        for asteroid in self.asteroids:

            if asteroid != station:

                delta_x = asteroid[0] - station[0]
                delta_y = station[1] - asteroid[1]

                vecs.setdefault(angle(delta_x, delta_y),[]).append((mag(delta_x, delta_y), asteroid))

        sorted_vecs = ((k, sorted(v)) for k, v in sorted(vecs.items()))

        idx = 0
        while True:
            for vec in sorted_vecs:
                print(vec)
                if len(vec[1]) > 0:
                    idx += 1
                    asteroid = vec[1].pop(0)
                    if idx == nth_vaporized:
                        return asteroid[1]

def test_part1(station):

    test_maps = [
        [
            '.#..#',
            '.....',
            '#####',
            '....#',
            '...##',
        ],
        [
            '......#.#.',
            '#..#.#....',
            '..#######.',
            '.#.#.###..',
            '.#..#.....',
            '..#....#.#',
            '#..#....#.',
            '.##.#..###',
            '##...#..#.',
            '.#....####',
        ],
        [
            '#.#...#.#.',
            '.###....#.',
            '.#....#...',
            '##.#.#.#.#',
            '....#.#.#.',
            '.##..###.#',
            '..#...##..',
            '..##....##',
            '......#...',
            '.####.###.',
        ],
        [
            '.#..#..###',
            '####.###.#',
            '....###.#.',
            '..###.##.#',
            '##.##.#.#.',
            '....###..#',
            '..#.#..#.#',
            '#..#.#.###',
            '.##...##.#',
            '.....#.#..',
        ],
        [
            '.#..##.###...#######',
            '##.############..##.',
            '.#.######.########.#',
            '.###.#######.####.#.',
            '#####.##.#.##.###.##',
            '..#####..#.#########',
            '####################',
            '#.####....###.#.#.##',
            '##.#################',
            '#####.##.###..####..',
            '..######..##.#######',
            '####.##.####...##..#',
            '.#####..#.######.###',
            '##...#.##########...',
            '#.##########.#######',
            '.####.#.###.###.#.##',
            '....##.##.###..#####',
            '.#.#.###########.###',
            '#.#.#.#####.####.###',
            '###.##.####.##.#..##',
        ]
    ]
    test_results = [
        (3,4,8),
        (5,8,33),
        (1,2,35),
        (6,3,41),
        (11,13,210),
    ]
    
    for test_map, test_result in zip(test_maps, test_results):

        station.load_map(test_map)
        (best_x, best_y, best_seen) = station.find_best_position()
        assert test_result == (best_x, best_y, best_seen)
    
    logging.info("Day 10: part 1 tests completed OK")

def test_part2(station):

    test_map = [
        '.#..##.###...#######',
        '##.############..##.',
        '.#.######.########.#',
        '.###.#######.####.#.',
        '#####.##.#.##.###.##',
        '..#####..#.#########',
        '####################',
        '#.####....###.#.#.##',
        '##.#################',
        '#####.##.###..####..',
        '..######..##.#######',
        '####.##.####...##..#',
        '.#####..#.######.###',
        '##...#.##########...',
        '#.##########.#######',
        '.####.#.###.###.#.##',
        '....##.##.###..#####',
        '.#.#.###########.###',
        '#.#.#.#####.####.###',
        '###.##.####.##.#..##',
    ]
    test_best_station = (11,13,210)
    nth = 200
    test_nth_vaporized = (8,2)

    station.load_map(test_map)
    (best_x, best_y, best_seen) = station.find_best_position()
    assert test_best_station == (best_x, best_y, best_seen)

    nth_vaporized = station.vaporize((best_x, best_y), nth)
    assert test_nth_vaporized == nth_vaporized

    logging.info("Day 10: part 2 tests completed OK")


def main():

    log_level = logging.INFO
    try:
        if int(sys.argv[1]):
            log_level = logging.DEBUG
    except (ValueError, IndexError):
        pass

    logging.basicConfig(
        level=log_level, format='%(levelname)-8s: %(message)s', datefmt='%H:%M:%S'
    )

    station = MonitoringStation()

    test_part1(station)
    test_part2(station)
    
    station.load_file('input_10.txt')
    (best_x, best_y, best_seen) = station.find_best_position()
    logging.info("Day 10: part 1: Station at location {} sees {} asteroids".format(
      (best_x, best_y), best_seen
    ))
    nth = 200
    nth_vaporized = station.vaporize((best_x, best_y), nth)
    coord = nth_vaporized[0]* 100 + nth_vaporized[1]
    logging.info("Day 10: part 2: Coordinates of {} asteroid vaporized yield result {}".format(
        nth, coord
    ))
    

if __name__ == '__main__':
    main()