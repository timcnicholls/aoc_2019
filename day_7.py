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

def test_part1():

    proc = IntCodeProcessor()

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

    logging.info("Day 7 part 1 self tests completed OK")

def part1():

    proc = IntCodeProcessor()
    #proc.self_test_basic()
    #proc.self_test_part1()
    #proc.self_test_part2()

    proc.load_file('input_7.txt')
    (max_thrust_signal, max_phase_sequence) = find_max_thrust(proc)
    logging.info("Part 1: max thrust signal {} found for phase sequence {}".format(
        max_thrust_signal, ','.join([str(phase) for phase in max_phase_sequence])
    ))


def find_max_thrust_feedback(test_program=None, program_file=None):

    num_procs = 5
    proc_names = ["A", "B", "C", "D", "E"]
    procs = []
    thrust_signal = {}

    # Create processors
    for idx in range(num_procs):
        procs.append(IntCodeProcessor(name=proc_names[idx], is_async=True))

    # Attach output queue of processor to next, and load program from appropriate source
    for idx in range(num_procs):

        procs[(idx+1) % num_procs].attach_input_queue(procs[idx].get_output_queue())
        if test_program:
            procs[idx].load_program(test_program)
        elif program_file:
            procs[idx].load_file(program_file)
        else:
            raise RuntimeError("No program input source specified")

    # Loop over all permutations of phase inputs sequences
    for phase_sequence in itertools.permutations([5,6,7,8,9]):
    #for phase_sequence in [(9,8,7,6,5)]:

        # Push the phase sequence element into the input queue of each processor
        for (idx, phase) in enumerate(phase_sequence):
            procs[idx].load_inputs([phase])

        # Prime the initial input value of the first processor
        procs[0].load_inputs([0])

        # Launch the processors in input threads
        proc_threads = []
        for idx in range(num_procs):
            proc_threads.append(procs[idx].run())

        # Wait for the threads to complete
        for proc_thread in proc_threads:
            proc_thread.join()

        # Get the final thrust value from the output queue of the last processor
        thrust = procs[-1].get_output_queue().get()
        thrust_signal[thrust] = phase_sequence

        for proc in procs:
            proc.reset_memory()

    max_thrust_signal = max(thrust_signal.keys())
    max_phase_sequence = thrust_signal[max_thrust_signal]
    
    logging.debug("Found max thrust signal {} for phase sequence {}".format(
        max_thrust_signal, ','.join([str(phase) for phase in max_phase_sequence])
    ))
    return (max_thrust_signal, max_phase_sequence)

def test_part2():

    test_phase_sequences = [
        (9,8,7,6,5),
        (9,7,8,5,6)
    ]
    test_max_thrusts = [
        139629729,
        18216
    ]
    test_programs = [
        [
            3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,
            27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5        
        ],
        [
            3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,
            -5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,
            53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10
        ]
    ]
    for test_phase_sequence, test_max_thrust, test_program in zip(
        test_phase_sequences, test_max_thrusts, test_programs
    ):
        (max_thrust, max_phase_sequence) = find_max_thrust_feedback(test_program=test_program)
        assert max_thrust == test_max_thrust
        assert max_phase_sequence == test_phase_sequence

    logging.info("Day 7 part 2 self tests completed OK")

def part2():

    (max_thrust_signal, max_phase_sequence) = find_max_thrust_feedback(program_file='input_7.txt')
    logging.info("Part 2: max thrust signal {} found for phase sequence {}".format(
        max_thrust_signal, ','.join([str(phase) for phase in max_phase_sequence])
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

    test_part1()
    part1()

    test_part2()
    part2()

if __name__ == '__main__':
    main()