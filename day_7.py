# AOC day 7

import itertools
import logging
import sys

from intcode import IntCodeProcessor

def find_max_thrust(proc):

    thrust_signal = {}

    for phase_sequence in itertools.permutations([0,1,2,3,4]):

        amp_input = 0

        for amp in range(5):
            
            proc.load_inputs([phase_sequence[amp], amp_input])
            proc.run()
            thrust = proc.get_outputs()[0]
            
            amp_input = thrust
            proc.reset_memory()

        thrust_signal[thrust] = phase_sequence

    max_thrust_signal = max(thrust_signal.keys())
    max_phase_sequence = thrust_signal[max_thrust_signal]
    
    logging.debug("Found max thrust signal {} for phase sequence {}".format(
        max_thrust_signal, ','.join([str(phase) for phase in max_phase_sequence])
    ))
    return (max_thrust_signal, max_phase_sequence)

def test_day7(proc):

    test_phase_sequences = [
        (4,3,2,1,0),
        (0,1,2,3,4),
        (1,0,4,3,2),
    ]
    test_max_thrusts = [
        43210,
        54321,
        65210
    ]
    test_programs = [
        [3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0],
        [3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0],
        [
            3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,
            1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0
        ]
    ]
    for test_phase_sequence, test_max_thrust, test_program in zip(
        test_phase_sequences, test_max_thrusts, test_programs
    ):

        proc.load_program(test_program)
        (max_thrust, phase_sequence) = find_max_thrust(proc)
        assert max_thrust == test_max_thrust
        assert phase_sequence == test_phase_sequence

    logging.info("Day 7 self tests completed OK")


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

    proc = IntCodeProcessor()
    #proc.self_test_basic()
    #proc.self_test_part1()
    #proc.self_test_part2()
    test_day7(proc)

    proc.load_file('input_7.txt')
    (max_thrust_signal, max_phase_sequence) = find_max_thrust(proc)
    logging.info("Part 1: max thrust signal {} found for phase sequence {}".format(
        max_thrust_signal, ','.join([str(phase) for phase in max_phase_sequence])
    ))


if __name__ == '__main__':
    main()