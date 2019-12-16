# AOC Day 13
import logging
import sys
import time

import numpy as np

class FlawedFrequencyTransmission():

    def __init__(self):

        self.input = None
        self.pattern = np.array([0, 1, 0, -1])
        self.pattern_len = len(self.pattern)

    def load_file(self, file_name):

        with open(file_name) as f:
            input_data = f.readlines()
            self.load_input(input_data[0].strip())

    def load_input(self, input_data):

        self.input = np.array([int(elem) for elem in input_data])

    def iterate(self, phases=1):

        # Copy input values to output array
        output_vals = np.copy(self.input)

        # Create array to hold working values during phase calculation
        phase_vals = np.empty(len(output_vals), dtype=int)

        # Loop over number of phases
        for phase in range(phases):

            # Loop over elements in output_vals
            for idx in range(len(output_vals)):
                
                # Expand the pattern according the element in the input we are at
                pos_pattern = np.repeat(self.pattern, idx+1)
 
                # Stretch pattern to match the length of the input
                if len(pos_pattern) <= len(output_vals):
                    scale = len(output_vals) // len(pos_pattern) + 1
                    pos_pattern = np.tile(pos_pattern, scale)

                # Truncate the pattern to remove the first value
                pos_pattern = np.array(pos_pattern[1:len(output_vals)+1])

                # Calculate phase value for this element
                phase_vals[idx] = np.abs(np.sum(pos_pattern * output_vals)) % 10

            # Copy values for elements after this phase to output
            output_vals = np.copy(phase_vals) 
            
        # Return first 8 elements of output value as string
        return ''.join([str(val) for val in output_vals[0:8]])

    def offset_iterate(self, phases=1):

        # Calculate offset based on first 8 elements of input
        offset = int(''.join([str(val) for val in self.input[0:7]]))

        # Expand the input data into the output and offset to message position
        output_vals = np.tile(self.input, 10000)
        output_vals = output_vals[offset:]

        # Loop over number of phases and calculate outputs. At a large offset, the
        # FFT becomes a simple sum of all the elements since the expanded pattern 
        # coefficients are all 1 - no need to iterate over all elements. This is done
        # in reverse so that we ignore the first half of the input in the cumulative sum.

        for phase in range(phases):
            
            phase_vals = np.cumsum(output_vals[::-1]) % 10
            output_vals = phase_vals[::-1]

        return ''.join([str(val) for val in output_vals[0:8]])

def test_part1(fft):

    input_signal = '12345678'

    for (phase, result) in enumerate(['48226158', '34040438', '03415518', '01029498']):
        fft.load_input(input_signal)
        output = fft.iterate(phase+1)
        assert output == result
    
    test_inputs = [
        '80871224585914546619083218645595',
        '19617804207202209144916044189917',
        '69317163492948606335995924319873',        
    ]
    test_outputs = [
        '24176176',
        '73745418',
        '52432133',
    ]

    for (test_input, test_output) in zip(test_inputs, test_outputs):

        fft.load_input(test_input)
        output = fft.iterate(100)
        assert output == test_output

    logging.info("Part 1: tests completed OK")

def part1(fft):

    output =fft.iterate(100)
    logging.info("Part 1: after 100 iterations, the output is: {}".format(output))

def test_part2(fft):

    test_inputs = [
        '03036732577212944063491565474664',
        '02935109699940807407585447034323',
        '03081770884921959731165446850517',
    ]
    test_outputs = [
        '84462026',
        '78725270',
        '53553731',
    ]

    for (test_input, test_output) in zip(test_inputs, test_outputs):

        fft.load_input(test_input)
        output = fft.offset_iterate(100)
        assert output == test_output

    logging.info("Part 2: tests completed OK")

def part2(fft):

    output = fft.offset_iterate(100)

    logging.info("Part 2: after 100 iterations the output message is {}".format(output))

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

    fft = FlawedFrequencyTransmission()
    
    test_part1(fft)
    test_part2(fft)

    fft.load_file('input/input_16.txt')

    part1(fft)
    part2(fft)

if __name__ == '__main__':
    main()