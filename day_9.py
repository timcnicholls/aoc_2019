# AOC day 9

import logging
import sys

from intcode import IntCodeProcessor

def test_part1(proc):
    
    test_programs = [
        [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99],
        [1102,34915192,34915192,7,4,7,99,0],
        [104,1125899906842624,99]
    ]

    test_inputs = [
        [],
        [],
        []
    ]
    test_outputs = [
        [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99],
        [1219070632396864],
        [1125899906842624]        
    ]

    for (test_program, test_input, test_output) in zip(
        test_programs, test_inputs, test_outputs
    ):  
        proc.load_program(test_program)
        if (len(test_input)):
            proc.load_input(test_input)

        proc.run()

        output = proc.get_outputs()
        assert test_output == output

    logging.info("Part 1: tests completed OK")

def part1(proc):
    
    proc.load_file('input_9.txt')
    proc.load_inputs([1])
    proc.run()
    output = proc.get_outputs()
    logging.info("Part 1: BOOST self test produced output: {}".format(output[0]))

def part2(proc):
    
    proc.reset_memory()
    proc.load_inputs([2])
    proc.run()
    output = proc.get_outputs()
    logging.info("Part 2: BOOST sensor mode located distress signal at coordinates: {}".format(
        output[0]
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

    proc = IntCodeProcessor(name='day9')

    test_part1(proc)

    proc.load_file('input_9.txt')
    part1(proc)
    part2(proc)

if __name__ == '__main__':
    main()