# AOC Day 15
import copy
import enum
import logging
import random
import queue
import sys
import time

from collections import defaultdict

from intcode import IntCodeProcessor

class WalkComplete(Exception):
    pass

class RepairDroid():

    class Direction(enum.IntEnum):
        NORTH = 1
        SOUTH = 2
        WEST = 3
        EAST = 4

    Directions = {
        Direction.NORTH: 'north', 
        Direction.SOUTH: 'south', 
        Direction.WEST:  'west', 
        Direction.EAST:  'east',
    }

    class Output(enum.IntEnum):
        UNKNOWN = -1
        WALL = 0
        MOVED = 1
        OXYGEN = 2

    Outputs = {
        Output.UNKNOWN: 'unknown',
        Output.WALL: 'wall',
        Output.MOVED: 'moved',
        Output.OXYGEN: 'oxygen system',
    }

    class Tile(enum.IntEnum):
        UNKNOWN = -1
        EMPTY = 0
        WALL = 1
        OXYGEN = 2
        DROID = 3

    Tiles = {
        Tile.UNKNOWN: ' ',
        Tile.EMPTY:  '.',
        Tile.WALL:   '#',
        Tile.OXYGEN: 'O',
        Tile.DROID:  'D',
    }


    MoveDelta = {
        Direction.NORTH: ( 0, -1),
        Direction.SOUTH: ( 0,  1),
        Direction.WEST:  (-1,  0),
        Direction.EAST:  ( 1,  0),
    }

    def __init__(self):

        self.proc = IntCodeProcessor(name='RepairDroid')

        self.tiles = defaultdict(lambda: self.Tile.UNKNOWN)
        self.visited = set()

        self.output_data = []
        self.coords = (0, 0)
        self.oxygen_coords = None
        self.direction_list = [
            self.Direction.NORTH, self.Direction.EAST, 
            self.Direction.SOUTH, self.Direction.WEST,
        ]
        self.direction_idx = 0

    def load_file(self, file_name):

        self.proc.load_file(file_name)

    def walk(self):

        def store_output(output_val):
            self.output_data.append(output_val)

        def coord_delta(coords, direction_idx):


            direction = self.direction_list[direction_idx]
            return tuple([sum(elems) for elems in zip(coords, self.MoveDelta[direction])])

        def process_move(status):

            oxygen_found = False

            if status == self.Output.WALL:
                
                self.tiles[coord_delta(self.coords, self.direction_idx)] = self.Tile.WALL
                self.direction_idx = (self.direction_idx + 1) % len(self.direction_list)

            else:

                if self.coords == self.oxygen_coords:
                    self.tiles[self.coords] = self.Tile.OXYGEN
                else:
                    self.tiles[self.coords] = self.Tile.EMPTY

                self.coords = coord_delta(self.coords, self.direction_idx)

                if status == self.Output.OXYGEN:
                    self.oxygen_coords = self.coords

                self.tiles[self.coords] = self.Tile.DROID
                self.visited.add(self.coords)

                if self.coords == (0,0):
                    raise WalkComplete
                self.direction_idx = (self.direction_idx + 3) % len(self.direction_list)

            self.display(status)

        def handle_input():

            # Start with a north move if no output data, i.e first input requested
            if len(self.output_data) == 0:
                
                self.direction_idx = 0
                self.tiles[self.coords] = self.Tile.EMPTY

            elif len(self.output_data) > 1:
                raise RuntimeError("Droid has reported more than one output move")

            else:
                process_move(self.output_data[0])

            self.output_data.clear()

            return self.direction_list[self.direction_idx]

        self.proc.attach_input_method(handle_input)
        self.proc.attach_output_method(store_output)

        try:
            self.proc.run()
        except WalkComplete:
            pass
        
        self.display(self.Output.OXYGEN, False)
        print("Walk completed, oxygen system is at {}".format(self.oxygen_coords))
        
    
    def find_shortest_path(self):

        return self.breadth_first((0,0), self.oxygen_coords)

    def find_fill_time(self):

        return self.breadth_first(self.oxygen_coords) - 1

    def breadth_first(self, start, end=None):

        distance = 0
        visited_set = set()
        current_set = {start}
        next_set = set()

        while True:

            for point in current_set:

                if point == end:
                    return distance

                visited_set.add(point)
                for dx, dy in self.MoveDelta.values():
                    x = point[0] + dx
                    y = point[1] + dy

                    if self.tiles[(x,y)] == self.Tile.WALL:
                        continue

                    neighbour = (x, y)

                    if neighbour in visited_set or neighbour in current_set:
                        continue

                    next_set.add(neighbour)

            current_set = next_set
            next_set = set()
            distance += 1

            if not current_set:
                break

        return distance

    def old_find_fill_time(self):

        start = self.oxygen_coords
        fill_time = 0
        visited_set = set()
        current_set = {start}
        next_set = set()

        while current_set:

            for point in current_set:

                visited_set.add(point)
                for dx, dy in self.MoveDelta.values():
                    x = point[0] + dx
                    y = point[1] + dy

                    if self.tiles[(x,y)] == self.Tile.WALL:
                        continue

                    neighbour = (x, y)

                    if neighbour in visited_set or neighbour in current_set:
                        continue

                    next_set.add(neighbour)

            current_set = next_set
            next_set = set()
            fill_time += 1

        return fill_time - 1

    def display(self, status, rewind=True):

        min_x = min((min([tile[0] for tile in self.tiles.keys()]), -20))
        max_x = max((max([tile[0] for tile in self.tiles.keys()]),  20))
        min_y = min((min([tile[1] for tile in self.tiles.keys()]), -20))
        max_y = max((max([tile[1] for tile in self.tiles.keys()]),  20))

        if self.oxygen_coords:
            self.tiles[self.oxygen_coords] = self.Tile.OXYGEN

        print("Droid coords: {} direction: {} status: {:20s}".format(
            self.coords, self.Directions[self.direction_list[self.direction_idx]], 
            self.Outputs[status]
        ))
        print("Tiles visited: {}".format(len(self.visited)))

        screen = '\n'.join(
            [''.join(
                ['X' if (x,y) == (0,0) else self.Tiles[self.tiles[(x,y)]] for x in range(min_x, max_x+1)]
            ) for y in range(min_y, max_y+1)]
        )
        print(screen)
        if rewind:
            screen_len = (max_y - min_y) + 3
            sys.stdout.write(u"\u001b[1000D") # Move left
            sys.stdout.write(u"\u001b[" + str(screen_len) + "A") # Move up       
        #time.sleep(1)

def part1(droid):

    droid.walk()
    shortest_path = droid.find_shortest_path()
    logging.info("Part 1: shortest path length to oxygen system is {}".format(shortest_path))

def part2(droid):

    fill_time = droid.find_fill_time()
    logging.info("Part 2: oxygen fill time is {}".format(fill_time))
 
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

    droid = RepairDroid()
    droid.load_file('input/input_15.txt')

    part1(droid)
    part2(droid)

if __name__ == '__main__':
    main()