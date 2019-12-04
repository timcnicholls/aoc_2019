# AOC Day 2

import logging

class IntCodeProcessor(object):

    def __init__(self, program=[]):

        self.program = program
        self.memory = []

        self.instruction_len = 4

        self.instructions = {
            1:  self._add,
            2:  self._multiply,
            99: self._halt,
        }
        self.reset_memory()

    def load_file(self, file_name):

        with open(file_name, 'r') as f:
            lines = f.readlines()

        self.program = []
        for line in lines:
            self.program.extend([int(val) for val in line.strip().split(',')])
        self.reset_memory()

    def load_program(self, program):

        self.program = program
        self.reset_memory()

    def reset_memory(self):

        self.memory = self.program.copy()
        self.memory_len = len(self.memory)

    def set_noun(self, noun):

        self.memory[1] = noun

    def set_verb(self, verb):

        self.memory[2] = verb

    def run(self):
        
        instruction_ptr = 0
        num_instructions = 0

        logging.debug('Running program of length {}'.format(self.memory_len))
        
        running = True

        while running and (instruction_ptr < self.memory_len):
            opcode = self.memory[instruction_ptr]
            try:
                running = self.instructions[opcode](instruction_ptr)
            except KeyError:
                raise RuntimeError(
                    "Invalid opcode {} at instruction pointer {}".format(
                    opcode, instruction_ptr
                ))
            instruction_ptr += self.instruction_len
            num_instructions += 1

        output = self.memory[0]
        logging.debug("Run completed after {} instructions with output {}".format(
            num_instructions, output
        ))
        return output

    def _add(self, ptr):
        (pos_op1, pos_op2, pos_result) = self.memory[ptr+1:ptr+4]
        self.memory[pos_result] = self.memory[pos_op1] + self.memory[pos_op2]
        logging.debug("  ADD : [{}]+[{}]=[{}] : {}+{}={}".format(
            pos_op1, pos_op2, pos_result,
            self.memory[pos_op1], self.memory[pos_op2], self.memory[pos_result]
        ))
        return True

    def _multiply(self, ptr):
        (pos_op1, pos_op2, pos_result) = self.memory[ptr+1:ptr+4]
        self.memory[pos_result] = self.memory[pos_op1] * self.memory[pos_op2]
        logging.debug("  MULT: [{}]+[{}]=[{}] : {}+{}={}".format(
            pos_op1, pos_op2, pos_result,
            self.memory[pos_op1], self.memory[pos_op2], self.memory[pos_result]
        ))
        return True

    def _halt(self, ptr):
        logging.debug("  HALT: ptr {}".format(ptr))
        return False

    def self_test(self):

        cases = [
            [1,9,10,3,2,3,11,0,99,30,40,50],
            [1,0,0,0,99] ,
            [2,3,0,3,99],
            [2,4,4,5,99,0],
            [1,1,1,4,99,5,6,0,99]
        ]

        results = [
            [3500,9,10,70,2,3,11,0,99,30,40,50],
            [2,0,0,0,99],
            [2,3,0,6,99],
            [2,4,4,5,99,9801],
            [30,1,1,4,2,5,6,0,99]
        ]

        for (case, result) in zip(cases, results):
            self.load_program(case)
            self.run()
            assert result == self.memory

def part1(proc):

    proc.set_noun(12)
    proc.set_verb(2)
    output = proc.run()
    logging.info("Part 1 : after running program, output is {}".format(output))

def part2(proc):

    desired_output = 19690720
    for noun in range(0, 100):
        for verb in range(0, 100):
            proc.reset_memory()
            proc.set_noun(noun)
            proc.set_verb(verb)
            output = proc.run()
            if output == desired_output:
                answer = (100 * noun) + verb
                logging.info("Part 2 : Noun {} verb {} gives output {} for answer {}".format(
                    noun, verb, output, answer
                ))
                break

def main():

    logging.basicConfig(
        level=logging.INFO, format='%(levelname)-8s: %(message)s', datefmt='%H:%M:%S'
    )

    proc = IntCodeProcessor()
    proc.self_test()

    proc.load_file('input_2.txt')

    part1(proc)
    part2(proc)


if __name__ == '__main__':
    main()