# AOC Day 17
import copy
import logging
import queue
import sys
import time

import numpy as np

from intcode import IntCodeProcessor

class TractorBeamDrone():
    
    def __init__(self):    
        self.proc = IntCodeProcessor(name='TractorBeamDrone')
        self.beam = None

    def load_file(self, file_name):

        self.proc.load_file(file_name)

    def profile_beam(self):

        max_x = 50
        max_y = 50

        self.beam = np.empty((max_y, max_x), dtype=int)

        for x in range(max_x):
            for y in range(max_y):
                
                self.proc.reset_memory()
                self.proc.load_inputs([x,y])
                self.proc.run()
                self.beam[y][x] = self.proc.get_outputs()[0]
        
        return np.sum(self.beam)

    def is_in_beam(self, x, y):

        self.proc.reset_memory()
        self.proc.load_inputs([x, y])
        self.proc.run()
        
        return self.proc.get_outputs()[0]

    def display_beam(self):

        (max_y, max_x) = self.beam.shape

        print('   : {}'.format(
            ''.join([str(x//10) for x in range(max_x)])
        ))
        print('   : {}'.format(
            ''.join([str(x%10) for x in range(max_y)])
        ))
        for y in range(max_y):
            line = ''.join(
                ['#' if self.beam[y][x] == 1 else '.' for x in range(max_x)]
            )
            print(f"{y:02d} : {line}")

    def fit_in_beam(self, size):

        # Find first affected point beyond (0,0)
        (first_y, first_x) = np.argwhere(self.beam==1)[1]
        logging.info(f"First point of beam beyond origin is at ({first_x},{first_y})")

        # Find first NxN fit top-right positions and store
        test_sizes = []
        top_x = []
        top_y = []
        (x, y) = (first_x, first_y)
        for test_size in range(2, 10):
            ((x, y), (dx, dy)) = self._find_fit(test_size, (x, y))
            test_sizes.append(test_size)
            top_x.append(x)
            top_y.append(y)

        # Git straight line top-right coordinates vs sizes
        (slope_x, int_x) = np.polyfit(test_sizes, top_x, 1)
        (slope_y, int_y) = np.polyfit(test_sizes, top_y, 1)

        # Calculate a starting point for the fit finder at the requested size - saves evaluating
        # every position down beam. Back off by one location to ensure that we find the first
        # position
        start_x = int(size*slope_x + int_x) - 1
        start_y = int(size*slope_y + int_y) - 1

        # Find the fit position for the specified size
        ((x, y), (dx, dy)) = self._find_fit(size, (start_x, start_y))
        
        # Return the caclulated position for the top-left corner, which is closest to the 
        # source
        return (dx * 10000) + y

    def _find_fit(self, size, start):

        (x, y) = start
        (dx, dy) = (0, 0)

        # Follow top edge of beam down from starting point until we find a site where
        # the beam accomodates a NxN shape of specified size. This is done by testing
        # that the bottom-left corner is also in the beam
        while True:
            x += 1
            while not self.is_in_beam(x, y): 
                y += 1
            
            (dx, dy) = (x-(size-1), y+(size-1))
            if self.is_in_beam(dx, dy):
                break

        return((x, y), (dx, dy))

def part1(drone):
    
    points_affected = drone.profile_beam()
    drone.display_beam()
    logging.info(f"Part 1: points affected by tractor beam: {points_affected}")

def part2(drone):
    
    size = 100
    location = drone.fit_in_beam(size)
    logging.info(f"Part 2: location where a ship of size ({size},{size}) fits in the beam: {location}")

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

    drone = TractorBeamDrone()
    drone.load_file('input/input_19.txt')

    part1(drone)
    part2(drone)

if __name__ == '__main__':
    main()