# AOC Day 13
import logging
import queue
import sys
import time

import numpy as np
from intcode import IntCodeProcessor

class BreakoutGame(object):

    Tiles = ['.', u'\u2588', '#', '=', 'o']
    
    def __init__(self):
        
        self.proc = IntCodeProcessor(name='Breakout')

        self.tiles = {}
        self.score = -1

        self.output_data = []

    def load_file(self, file_name):

        self.proc.load_file(file_name)

    def enable_free_play(self):

        self.proc.memory[0] = 2

    def run(self, interactive=False):

        self.tiles = {}

        if not interactive:
            self.proc.run()
            outputs = self.proc.get_outputs()

            for idx in range(0, len(outputs), 3):
                (x, y, tile_id) = outputs[idx:idx+3]
                self.tiles[(x, y)] = tile_id

        else:

            self.paddle_pos = None
            self.ball_pos = None
            self.tiles_output = 0
            self.initialized = False

            def store_output(output_val):
                self.output_data.append(output_val)

            def process_output():
                
                for idx in range(0, len(self.output_data), 3):
                    (x, y, tile_id) = self.output_data[idx:idx+3]

                    if x == -1 and y == 0:
                        self.score = tile_id
                    else:
                        self.tiles[(x, y)] = tile_id
                        if not self.initialized:
                            self.tiles_output += 1
                            if self.tiles_output >= 1008:
                                self.initialized = True

                        if tile_id == 3:
                            self.paddle_pos = x

                        if tile_id == 4:
                            self.ball_pos = x
                            if self.initialized:
                                self.display()

            def handle_input():

                process_output()
                if self.paddle_pos > self.ball_pos:
                    joystick = -1
                elif self.paddle_pos == self.ball_pos:
                    joystick = 0
                else:
                    joystick = 1
                
                self.output_data.clear()
                return joystick

            self.proc.attach_input_method(handle_input)
            self.proc.attach_output_method(store_output)
            self.proc.run()
            process_output()

    def get_num_blocks(self):

        return sum(1 for k, v in self.tiles.items() if v==2)

    def get_score(self):

        return self.score

    def display(self):

        min_x = min([tile[0] for tile in self.tiles.keys()])
        max_x = max([tile[0] for tile in self.tiles.keys()])
        min_y = min([tile[1] for tile in self.tiles.keys()])
        max_y = max([tile[1] for tile in self.tiles.keys()])

        screen = '\n'.join(
            [''.join(
                [self.Tiles[self.tiles[(x,y)]] for x in range(min_x, max_x+1)]
            ) for y in range(min_y, max_y+1)]
        )
        print(screen)
        print("Score: {}".format(self.score))
        screen_len = (max_y - min_y) + 2 
        sys.stdout.write(u"\u001b[1000D") # Move left
        sys.stdout.write(u"\u001b[" + str(screen_len) + "A") # Move up
        time.sleep(0.05)
        
def part1():

    game = BreakoutGame()
    game.load_file('input_13.txt')
    game.run(interactive=False)
    num_blocks = game.get_num_blocks()
    logging.info("Part 1: number of block tiles output is {}".format(num_blocks))

def part2():

    game = BreakoutGame()
    game.load_file('input_13.txt')
    game.enable_free_play()
    game.run(interactive=True)
    logging.info("Part 2: score at end of game is {}".format(game.get_score()))

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

    #part1()
    part2()
    

if __name__ == '__main__':
    main()