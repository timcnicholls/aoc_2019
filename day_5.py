# AOC Day 5

import enum
import logging

class IntCodeProcessor(object):

    class Opcode(enum.IntEnum):
        ADD = 1
        MULTIPLY = 2
        INPUT = 3
        OUTPUT = 4
        JUMP_TRUE = 5
        JUMP_FALSE = 6
        LESS_THAN = 7
        EQUALS = 8
        HALT = 99

    class ParamMode(enum.IntEnum):
        POSITION = 0
        IMMEDIATE = 1

    def __init__(self, program=[]):

        self.program = program
        self.memory = []
        self.inputs = []
        self.outputs = []

        self.instructions = {
            self.Opcode.ADD:        (self._add, 4),
            self.Opcode.MULTIPLY:   (self._multiply, 4),
            self.Opcode.INPUT:      (self._input, 2),
            self.Opcode.OUTPUT:     (self._output, 2),
            self.Opcode.JUMP_TRUE:  (self._jump_true, 0),
            self.Opcode.JUMP_FALSE: (self._jump_false, 0),
            self.Opcode.LESS_THAN:  (self._less_than, 4),
            self.Opcode.EQUALS:     (self._equals, 4),
            self.Opcode.HALT:       (self._halt, 1),
        }
        self.max_instruction_len = max([ins[1] for ins in self.instructions.values()])
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

    def load_inputs(self, inputs):

        logging.debug("Loading inputs of length {}: {}".format(len(inputs), inputs))
        self.inputs = inputs

    def get_outputs(self):
        return self.outputs

    def reset_memory(self):

        self.memory = self.program.copy()
        self.memory_len = len(self.memory)

    def set_noun(self, noun):

        self.memory[1] = noun

    def set_verb(self, verb):

        self.memory[2] = verb

    def run(self):
        
        self.instruction_ptr = 0
        self.outputs = []

        logging.debug('Running program of length {}'.format(self.memory_len))
        
        running = True
        num_instructions = 0

        while running and (self.instruction_ptr < self.memory_len):

            (opcode, param_modes) = self._parse_instruction(self.memory[self.instruction_ptr])
            logging.debug("  ptr {} mem {} opcode {} param_modes {}".format(
                self.instruction_ptr, self.memory[self.instruction_ptr], opcode, param_modes
            ))

            try:
                (instruction, instruction_len) = self.instructions[opcode]
                running = instruction(self.instruction_ptr, param_modes)
            except KeyError:
                raise RuntimeError(
                    "Invalid opcode {} at instruction pointer {}".format(
                    opcode, self.instruction_ptr
                ))
            self.instruction_ptr += instruction_len
            num_instructions += 1

        output = self.memory[0]
        logging.debug("Run completed after {} instructions with output {}".format(
            num_instructions, output
        ))
        return output

    def _parse_instruction(self, instruction):
        
        opcode = (instruction % 100)
        param_modes = [self.ParamMode.POSITION] * (self.max_instruction_len - 1)

        remainder = instruction // 100
        param_idx = 0
        while remainder > 0:
            param_modes[param_idx] =  self.ParamMode(remainder % 10)
            remainder = remainder // 10
            param_idx += 1
    
        return (opcode, param_modes)

    def _resolve_params(self, ptr, num_params, param_modes):
        
        params = []
        for idx in range(num_params):
            pos_param = self.memory[ptr + 1 + idx]
            if param_modes[idx] == self.ParamMode.POSITION:
                params.append(self.memory[pos_param])
            elif param_modes[idx] == self.ParamMode.IMMEDIATE:
                params.append(pos_param)

        return params

    def _add(self, ptr, param_modes):

        assert self.ParamMode.POSITION == param_modes[2]

        params = self._resolve_params(ptr, 2, param_modes)
        pos_result = self.memory[ptr+3]

        self.memory[pos_result] = params[0] + params[1]

        logging.debug("  ADD : [{}]+[{}]=[{}] : {}+{}={}".format(
            ptr+1, ptr+2, pos_result,
            params[0], params[1], self.memory[pos_result]
        ))
        return True

    def _multiply(self, ptr, param_modes):

        assert self.ParamMode.POSITION == param_modes[2]

        params = self._resolve_params(ptr, 2, param_modes)
        pos_result = self.memory[ptr+3]
        result =params[0] * params[1]

        logging.debug("  MULT: [{}]+[{}]=[{}] : {}+{}={}".format(
            ptr+1, ptr+2, pos_result,
            params[0], params[1], result
        ))
        self.memory[pos_result] = result

        return True

    def _input(self, ptr, param_modes):

        input_val = self.inputs.pop(0)
        pos_input = self.memory[ptr + 1]
        logging.debug("  INPUT: ptr {} [{}]={}".format(ptr, pos_input, input_val))
        self.memory[pos_input] = input_val

        return True

    def _output(self, ptr, param_modes):
        
        output_val = self._resolve_params(ptr, 1, param_modes)[0]
        logging.debug("  OUTPUT: ptr {} [{}]={}".format(ptr, ptr+1, output_val))
        self.outputs.append(output_val)

        return True

    def _jump_true(self, ptr, param_modes):
        
        self._jump_condition(ptr, param_modes, True)
        return True

    def _jump_false(self, ptr, param_modes):

        self._jump_condition(ptr, param_modes, False)
        return True

    def _jump_condition(self, ptr, param_modes, condition):

        params = self._resolve_params(ptr, 2, param_modes)
        logging.debug("  JUMP_{}: ptr {} val {} ins_ptr {}".format(
            str(condition).upper(), ptr, params[0], params[1]
        ))

        if (params[0] != 0) == condition: 
            self.instruction_ptr = params[1]
        else:
            self.instruction_ptr += 3
        pass

    def _less_than(self, ptr, param_modes):

        assert self.ParamMode.POSITION == param_modes[2]

        params = self._resolve_params(ptr, 2, param_modes)
        pos_result = self.memory[ptr+3]

        self.memory[pos_result] = int(params[0] < params[1])

        logging.debug("  LESS THAN : [{}]=[{}]=[{}] : {}+{}={}".format(
            ptr+1, ptr+2, pos_result,
            params[0], params[1], self.memory[pos_result]
        ))

        return True

    def _equals(self, ptr, param_modes):

        assert self.ParamMode.POSITION == param_modes[2]

        params = self._resolve_params(ptr, 2, param_modes)
        pos_result = self.memory[ptr+3]

        self.memory[pos_result] = int(params[0] == params[1])

        logging.debug("  EQUALS : [{}]=[{}]=[{}] : {}+{}={}".format(
            ptr+1, ptr+2, pos_result,
            params[0], params[1], self.memory[pos_result]
        ))

        return True

    def _halt(self, ptr, param_modes):
        logging.debug("  HALT: ptr {}".format(ptr))
        return False

    def run_self_test_cases(self, test_cases, test_results=[], test_inputs=[], test_outputs=[]):

        if len(test_results) == 0:
            test_results = []*len(test_cases)
        if len(test_inputs) == 0:
            test_inputs = []*len(test_cases)
        if len(test_outputs) == 0:
            test_outputs = []*len(test_cases)

        for (test_case, test_result, test_input, test_output) in zip(
            test_cases, test_results, test_inputs, test_outputs):
            self.load_program(test_case)
            if len(test_input):
                self.load_inputs(test_input)
            self.run()
            if len(test_result):
                assert test_result == self.memory
            else:
                print(self.memory)
            if len(test_output):
                assert test_output == self.get_outputs()

    def self_test_basic(self):

        test_cases = [
            [1,9,10,3,2,3,11,0,99,30,40,50],
            [1,0,0,0,99] ,
            [2,3,0,3,99],
            [2,4,4,5,99,0],
            [1,1,1,4,99,5,6,0,99]
        ]

        test_results = [
            [3500,9,10,70,2,3,11,0,99,30,40,50],
            [2,0,0,0,99],
            [2,3,0,6,99],
            [2,4,4,5,99,9801],
            [30,1,1,4,2,5,6,0,99]
        ]

        self.run_self_test_cases(test_cases, test_results)

    def self_test_part1(self):

        # Test instruction parsing
        instruction = 1002
        (opcode, param_modes) = self._parse_instruction(instruction)
        assert opcode == self.Opcode.MULTIPLY
        assert param_modes == [self.ParamMode.POSITION, self.ParamMode.IMMEDIATE, self.ParamMode.POSITION]

        test_cases = [
            [3,0,4,0,99],
            [1002,4,3,4,33],
        ]
        test_inputs = [
            [1234],
            []
        ]
        test_outputs = [
            [1234],
            []
        ]
        test_results = [
            [1234,0,4,0,99],
            [1002,4,3,4,99]
        ]
        self.run_self_test_cases(test_cases, test_results, test_inputs, test_outputs)

    def self_test_part2(self):

        test_cases = [
            [3,9,8,9,10,9,4,9,99,-1,8],  # Test input = 8, position mode
            [3,9,8,9,10,9,4,9,99,-1,8],  # Test input = 8, position mode
            [3,9,7,9,10,9,4,9,99,-1,8],  # Test input < 8, position mode
            [3,9,7,9,10,9,4,9,99,-1,8],  # Test input < 8, position mode
            [3,3,1108,-1,8,3,4,3,99],    # Test input = 8, immediate mode
            [3,3,1108,-1,8,3,4,3,99],    # Test input = 8, immediate mode
            [3,3,1107,-1,8,3,4,3,99],    # Test input < 8, immediate mode
            [3,3,1107,-1,8,3,4,3,99],    # Test input < 8, immediate mode
            [3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9], # Jump test, output = (input != 0), position mode
            [3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9], # Jump test, output = (input != 0), position mode
            [3,3,1105,-1,9,1101,0,0,12,4,12,99,1], # Jump test, output = (input != 0), immediate mode
            [3,3,1105,-1,9,1101,0,0,12,4,12,99,1], # Jump test, output = (input != 0), immediate mode
        ]
        test_inputs = [
            [8],
            [7],
            [7],
            [9],
            [8],
            [7],
            [7],
            [9],
            [0],
            [17],
            [0],
            [17],
        ]
        test_outputs = [
            [1],
            [0],
            [1],
            [0],
            [1],
            [0],
            [1],
            [0],
            [0],
            [1],
            [0],
            [1]
        ]
        test_results = [
            [3,9,8,9,10,9,4,9,99,1,8],
            [3,9,8,9,10,9,4,9,99,0,8],
            [3,9,7,9,10,9,4,9,99,1,8],
            [3,9,7,9,10,9,4,9,99,0,8],
            [3,3,1108,1,8,3,4,3,99],
            [3,3,1108,0,8,3,4,3,99],
            [3,3,1107,1,8,3,4,3,99],
            [3,3,1107,0,8,3,4,3,99],
            [3,12,6,12,15,1,13,14,13,4,13,99,0,0,1,9],
            [3, 12, 6, 12, 15, 1, 13, 14, 13, 4, 13, 99, 17, 1, 1, 9],
            [3, 3, 1105, 0, 9, 1101, 0, 0, 12, 4, 12, 99, 0],
            [3, 3, 1105, 17, 9, 1101, 0, 0, 12, 4, 12, 99, 1],
        ]
        self.run_self_test_cases(test_cases, test_results, test_inputs, test_outputs)

        test_cases = [
            3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
            1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
            999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99
        ]*3

        test_inputs = [[7], [8], [9]]

        test_outputs = [[999], [1000], [1001]]

        test_results = []
        self.run_self_test_cases(test_cases, test_results, test_inputs, test_outputs)

def part1(proc):

    proc.reset_memory()

    inputs = [1]
    proc.load_inputs(inputs)
    proc.run()
    outputs = proc.get_outputs()

    outcome = "PASSED" if sum(outputs[:-1]) == 0 else "FAILED"
    logging.info("Part 1: TEST diagnostic {} with code {}".format(
        outcome, outputs[-1]
    ))

def part2(proc):
    
    proc.reset_memory()
    
    inputs = [5]
    proc.load_inputs(inputs)
    proc.run()
    diagnostic_code = proc.get_outputs()[0]
    logging.info("Part 2: Test diagnostic produced code {}".format(
        diagnostic_code
    ))

def main():

    logging.basicConfig(
        level=logging.INFO, format='%(levelname)-8s: %(message)s', datefmt='%H:%M:%S'
    )

    proc = IntCodeProcessor()
    proc.self_test_basic()
    proc.self_test_part1()
    proc.self_test_part2()

    proc.load_file('input_5.txt')
    part1(proc)
    part2(proc)


if __name__ == '__main__':
    main()