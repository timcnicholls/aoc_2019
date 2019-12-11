# AOC Day 11
import enum
import logging
import queue
import sys
import threading

from collections import defaultdict

from intcode import IntCodeProcessor

class HullPaintingRobot(object):

    class Direction(enum.IntEnum):

        UP = 0
        RIGHT = 1
        DOWN = 2
        LEFT = 3

    class Turn(enum.IntEnum):

        LEFT = 0
        RIGHT = 1

    def __init__(self, program_file):

        self.proc = IntCodeProcessor(name='Robot', is_async=True)
        self.input_queue = queue.Queue()
        self.proc.attach_input_queue(self.input_queue)
        self.output_queue = self.proc.get_output_queue()
        
        self.painted_panels = defaultdict(lambda: 0)
        self.panel_coords = (0,0)
        self.direction = self.Direction.UP

        self.move_ops = {
            self.Direction.UP    : ( 0, -1),
            self.Direction.DOWN  : ( 0,  1),
            self.Direction.LEFT  : (-1,  0),
            self.Direction.RIGHT : ( 1,  0),
        }
        self.num_moves = len(self.move_ops)

        self.proc.load_file(program_file)

    def move(self, turn):

        op = 0
        if turn == self.Turn.LEFT:
            op = -1
        elif turn == self.Turn.RIGHT:
            op = 1
        else:
            raise RunTimeError("Illegal turn direction {} specified".format(turn))
        self.direction = self.Direction((self.direction + op) % self.num_moves)

        self.panel_coords = tuple(sum(elem) for elem in zip(
            self.panel_coords, self.move_ops[self.direction]
        ))
        logging.debug("ROBOT move: turn {} direction {} coords {}".format(
            turn, self.direction.name, self.panel_coords
        ))
        
    def run(self, initial_panel_colour):

        self.proc.run()

        current_panel_colour = initial_panel_colour
        moves_made = 0

        while self.proc.running:

            self.input_queue.put(current_panel_colour)
            try:
                (colour, turn) = (self.output_queue.get(timeout=1.0), self.output_queue.get(timeout=1.0))
            except queue.Empty:
                if self.proc.running:
                    raise RunTimeError("ROBOT processor timed out")
                else:
                    logging.debug("ROBOT processor halted")
                    break

            logging.debug("ROBOT got instructions: colour {} turn {}".format(
                colour, turn
            ))

            self.painted_panels[self.panel_coords] = colour
            logging.debug("ROBOT painted panel {} {}".format(
                self.panel_coords, 'WHITE' if colour else 'BLACK'
            ))
            self.move(turn)
            moves_made += 1
            current_panel_colour = self.painted_panels[self.panel_coords]            

        return (moves_made, len(self.painted_panels))

    def show_registration(self):
        
        min_x = None
        max_x = None
        min_y = None
        max_y = None

        for (x, y) in self.painted_panels.keys():

            if min_x is None or x < min_x:
                min_x = x
            if max_x is None or x > max_x:
                max_x = x
            if min_y is None or y < min_y:
                min_y = y
            if max_y is None or y > max_y:
                max_y = y

        logging.info("Registration code:\n")
        
        for y in range(min_y, max_y+1):
            row = '  >'
            for x in range(min_x, max_x+1):
                char = '#' if self.painted_panels[(x,y)] == 1 else ' '
                row = row + char
            logging.info(row)

def part1():

    robot = HullPaintingRobot('input_11.txt')
    (moves_made, painted_panels) = robot.run(0)

    logging.info("Part 1: robot finished painting after {} moves painting {} panels".format(
        moves_made, painted_panels
    ))

def part2():

    robot = HullPaintingRobot('input_11.txt')
    (moves_made, painted_panels) = robot.run(1)

    logging.info("Part 2: robot finished painting after {} moves painting {} panels".format(
        moves_made, painted_panels
    ))
    robot.show_registration()

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

    part1()
    part2()
    

if __name__ == '__main__':
    main()