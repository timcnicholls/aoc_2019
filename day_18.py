# AOC day 18

import logging
import sys

class TritonMaze():

    def __init__(self):

        self.maze = {}
        self.rows = 0
        self.cols = 0
        self.starts = None
        self.seen = {}

        self.adjacents = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    def load_file(self, file_name):

        with open(file_name) as f:
            input_data = f.readlines()
            self.load_input(input_data)

    def load_input(self, input_data):

        for y, line in enumerate(input_data):
            for x, elem in enumerate(line.strip()):
                self.maze[(x,y)] = elem

        self.rows = y + 1
        self.cols = x + 1

        self.starts = [coord for coord, val in self.maze.items() if val == '@']
        if len(self.starts) == 0:
            raise RuntimeError("No start positions found in maze")

        self.keys_in_maze = sorted([elem for elem in self.maze.values() if 'a' <= elem <= 'z'])
        self.doors_in_maze = sorted([elem for elem in self.maze.values() if 'A' <= elem <= 'Z'])

        self.seen = {}

        logging.debug(
            "Loaded maze of size {} x {} with {} start(s), {} keys and {} doors".format(
                self.rows, self.cols, len(self.starts), len(self.keys_in_maze), len(self.doors_in_maze)
            )
        )

    def reachable_keys(self, start, existing_keys):
        
        distance = {start: 0}
        keys = {}

        current_set = {start}
        next_set = set()

        while current_set:

            for point in current_set:

                for dx, dy in self.adjacents:
                    x = point[0] + dx
                    y = point[1] + dy
                    
                    if not ((0 <= x < self.cols) and (0 <= y < self.rows)):
                        continue

                    neighbour = (x,y)
                    elem = self.maze[neighbour]
                    if elem == '#':
                        continue
                    
                    if neighbour in distance:
                        continue

                    distance[neighbour] = distance[point] + 1

                    if 'A' <= elem <= 'Z' and elem.lower() not in existing_keys:
                        continue

                    if 'a' <= elem <= 'z' and elem not in existing_keys:
                        keys[elem] = distance[neighbour], neighbour
                    else:
                        next_set.add(neighbour)

            current_set = next_set
            next_set = set()

        return keys

    def shortest_path(self, start=None, existing_keys=[]):

        if start is None:
            start = self.starts[0]

        existing_key_str = ''.join(sorted(existing_keys))
        logging.debug(f"Shortest path entry: start {start} existing_keys {existing_keys} {existing_key_str}")

        if (start, existing_key_str) in self.seen:
            return self.seen[start, existing_key_str]

        keys = self.reachable_keys(start, existing_keys)
        logging.debug("From position {} keys reachable are: {}".format(start, keys))
        if len(keys) == 0:
            logging.debug(f"No keys reachable from start {start} existing keys {existing_key_str}")
            return 0

        possible_paths = []
        for key, (distance, point) in keys.items():
            logging.debug(f"Loop over possible: key: {key} distance: {distance} point: {point}")
            possible_paths.append(distance + self.shortest_path(point, existing_keys + [key]))
        
        min_path = min(possible_paths)
        self.seen[start, existing_key_str] = min_path

        logging.debug(f"Minimum path is {min_path}")
        return min_path

    def parallel_reachable_keys(self, starts, existing_keys):

        keys = {}
        for idx, start in enumerate(starts):
            for key, (distance, point) in self.reachable_keys(start, existing_keys).items():
                keys[key] = distance, point, idx

        return keys

    def parallel_shortest_path(self, starts=None, existing_keys=[]):
        
        if starts is None:
            starts = tuple(self.starts)

        existing_key_str = ''.join(sorted(existing_keys))

        if (starts, existing_key_str) in self.seen:
            return self.seen[starts, existing_key_str]

        keys = self.parallel_reachable_keys(starts, existing_keys)
        if len(keys) == 0:
            logging.debug(
                f"No keys reachable from starts {starts} with existing keys {existing_key_str}"
            )
            return 0

        possible_paths = []
        for key, (distance, point, idx) in keys.items():
            parallel_starts = tuple(point if i == idx else p for i, p in enumerate(starts))
            logging.debug(
                f"Parallel loop over possible: key: {key} distance: {distance} starts: {parallel_starts}"
            )
            possible_paths.append(
                distance + self.parallel_shortest_path(parallel_starts, existing_keys + [key])
            )
        min_path = min(possible_paths)
        self.seen[starts, existing_key_str] = min_path

        logging.debug(f"Minimum path is {min_path}")
        return min_path

def test_part1(maze):
    
    test_mazes = [
        [
            '#########',
            '#b.A.@.a#',
            '#########',
        ],
        [
            '########################',
            '#f.D.E.e.C.b.A.@.a.B.c.#',
            '######################.#',
            '#d.....................#',
            '########################',
        ],
        [
            '########################',
            '#...............b.C.D.f#',
            '#.######################',
            '#.....@.a.B.c.d.A.e.F.g#',
            '########################',
        ],
        [
            '#################',
            '#i.G..c...e..H.p#',
            '########.########',
            '#j.A..b...f..D.o#',
            '########@########',
            '#k.E..a...g..B.n#',
            '########.########',
            '#l.F..d...h..C.m#',
            '#################',
        ],
        [
            '########################',
            '#@..............ac.GI.b#',
            '###d#e#f################',
            '###A#B#C################',
            '###g#h#i################',
            '########################',
        ]
    ]

    test_shortest_paths = [
        8, 86, 132, 136, 81
    ]

    for (test_maze, test_shortest_path) in zip(test_mazes, test_shortest_paths):

        maze.load_input(test_maze)
        shortest_path = maze.shortest_path()
        assert test_shortest_path == shortest_path

    logging.info("Part 1: tests completed OK")

def test_part2(maze):

    test_mazes = [
        [
            '#######',
            '#a.#Cd#',
            '##@#@##',
            '#######',
            '##@#@##',
            '#cB#Ab#',
            '#######',
        ],
        [
            '###############',
            '#d.ABC.#.....a#',
            '######@#@######',
            '###############',
            '######@#@######',
            '#b.....#.....c#',
            '###############',
        ],
        [
            '#############',
            '#DcBa.#.GhKl#',
            '#.###@#@#I###',
            '#e#d#####j#k#',
            '###C#@#@###J#',
            '#fEbA.#.FgHi#',
            '#############',
        ],
        [
            '#############',
            '#g#f.D#..h#l#',
            '#F###e#E###.#',
            '#dCba@#@BcIJ#',
            '#############',
            '#nK.L@#@G...#',
            '#M###N#H###.#',
            '#o#m..#i#jk.#',
            '#############',
        ],
    ]

    test_shortest_paths = [
        8, 24, 32, 72
    ]
    for (test_maze, test_shortest_path) in zip(test_mazes, test_shortest_paths):

        maze.load_input(test_maze)
        shortest_path = maze.parallel_shortest_path()
        assert test_shortest_path == shortest_path

    logging.info("Part 2: tests completed OK")

def part1(maze):
    
    maze.load_file('input/input_18.txt')
    shortest_path = maze.shortest_path()
    logging.info(f"Part 1: the shortest path through the maze has length {shortest_path}")

def part2(maze):
    
    maze.load_file('input/input_18_pt2.txt')
    shortest_path = maze.parallel_shortest_path()
    logging.info(f"Part 2: the fewest steps to collect all keys in parallel is {shortest_path}")

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

    maze = TritonMaze()
    
    test_part1(maze)
    test_part2(maze)

    part1(maze)
    part2(maze)

if __name__ == '__main__':
    main()