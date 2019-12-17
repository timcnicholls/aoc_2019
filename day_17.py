# AOC Day 17
import copy
import logging
import queue
import sys
import time

from intcode import IntCodeProcessor

class AsciiRobot():


    CRLF     = ord('\n')
    SCAFFOLD = ord('#')
    SPACE    = ord('.')
    INTERSECTION = ord('O')

    def __init__(self):

        self.proc = IntCodeProcessor(name='AsciiRobot')

        self.scaffold = []
        self.rows = 0
        self.cols = 0
        self.intersections = set()

    def load_file(self, file_name):

        self.proc.load_file(file_name)

    def draw(self):

        self.proc.run()
        
        row = []
        for elem in  self.proc.get_outputs():
            if elem == self.CRLF and len(row):
                self.scaffold.append(copy.deepcopy(row))
                row.clear()
            else:
                row.append(elem)

        self.rows = len(self.scaffold)
        self.cols = len(self.scaffold[0])
        print("Scaffold rows: {} columns: {}".format(self.rows, self.cols))


    def display_scaffold(self):

        disp_scaff = copy.deepcopy(self.scaffold)
        for (x, y) in self.intersections:
            disp_scaff[y][x] = self.INTERSECTION

        print('   : {}'.format(
            ''.join([str(x//10) for x in range(self.cols)])
        ))
        print('   : {}'.format(
            ''.join([str(x%10) for x in range(self.cols)])
        ))
        for y, row in enumerate(disp_scaff):
            print('{:2d} : {}'.format(y, ''.join([chr(elem) for elem in row])))


    def calculate_alignment(self):

        alignment = 0
        self.intersections.clear()

        for y, row in enumerate(self.scaffold):
            for x, elem in enumerate(row):
                if elem == self.SCAFFOLD:
                    ok = True
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        xx, yy = x + dx, y + dy
                        if 0 <= yy < self.rows and 0 <= xx < self.cols and self.scaffold[yy][xx] != self.SCAFFOLD:
                            ok = False
                            break

                    if ok:
                        self.intersections.add((x, y))
                        alignment += x * y

        return alignment

    def num_intersections(self):

        return len(self.intersections)

    def run(self, input):

        self.proc.memory[0] = 2
        self.proc.load_inputs(input)
        self.proc.run()
        
        dust_collected = self.proc.get_outputs()[-1]
        return dust_collected

def part1():

    robot = AsciiRobot()
    robot.load_file('input/input_17.txt')
    robot.draw()

    alignment = robot.calculate_alignment()
    num_intersections = robot.num_intersections()
    robot.display_scaffold()
    logging.info("Part 1: scaffold robot camera has {} intersections and alignment {}".format(
        num_intersections, alignment
    ))

def part2():

    input_ascii = [
        "A,B,A,C,B,C,B,C,A,C",
        "R,12,L,10,R,12",
        "L,8,R,10,R,6",
        "R,12,L,10,R,10,L,8",
        "n\n"
    ]

    input_code = [ord(char) for char in '\n'.join(input_ascii)]

    robot = AsciiRobot()
    robot.load_file('input/input_17.txt')
    dust_collected = robot.run(input_code)

    logging.info("Part 2: scaffold robot reports amount of dust collected: {}".format(
        dust_collected
    ))


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