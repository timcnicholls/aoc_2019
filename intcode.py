# Advent of code 2019 IntCode processor

import enum
import logging
import operator
import queue
import sys
import threading

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
        ADJ_REL = 9
        HALT = 99

    class ParamMode(enum.IntEnum):
        POSITION = 0
        IMMEDIATE = 1
        RELATIVE = 2

    OpSymbols = {
        'add': '+',
        'mul': '*',
        'eq':  '==',
        'lt':  '<',
    }

    def __init__(self, program=[], name="IntCode", is_async=False):

        self.program = program
        self.name = name
        self.is_async = is_async

        self.memory = []
        self.inputs = []
        self.outputs = []
        self.input_queue = None
        self.output_queue = queue.Queue()
        self.input_method = None
        self.output_method = None

        self.run_thread = None

        self.diagnostic_debug = False

        self.relative_base = 0

        self.instructions = {
            self.Opcode.ADD:        (self._add, 4),
            self.Opcode.MULTIPLY:   (self._multiply, 4),
            self.Opcode.INPUT:      (self._input, 2),
            self.Opcode.OUTPUT:     (self._output, 2),
            self.Opcode.JUMP_TRUE:  (self._jump_true, 3),
            self.Opcode.JUMP_FALSE: (self._jump_false, 3),
            self.Opcode.LESS_THAN:  (self._less_than, 4),
            self.Opcode.EQUALS:     (self._equals, 4),
            self.Opcode.ADJ_REL:    (self._adjust_relative, 2),
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
        if self.is_async:
            [self.input_queue.put(val) for val in inputs]
        else:
            self.inputs = inputs

    def get_outputs(self):
        return self.outputs

    def reset_memory(self):

        self.memory = self.program.copy()
        self.memory_len = len(self.memory)

        self.relative_base = 0

    def set_noun(self, noun):

        self.memory[1] = noun

    def set_verb(self, verb):

        self.memory[2] = verb

    def attach_input_queue(self, input_queue):

        self.input_queue = input_queue

    def get_output_queue(self):

        return self.output_queue

    def attach_input_method(self, input_method):

        self.input_method = input_method
    
    def attach_output_method(self, output_method):

        self.output_method = output_method

    def run(self):

        if self.is_async:
            self.run_thread = threading.Thread(target=self._run)
            self.run_thread.start()
            logging.debug("Processor {} starting in thread".format(self.name))
            return self.run_thread
        else:
            output = self._run()
            return output

    def _run(self):
        
        logging.debug('Running program of length {}'.format(self.memory_len))
        
        self.instruction_ptr = 0
        self.outputs = []
        self.running = True
        num_instructions = 0

        # Loop over the instructions in memory while HALT has not been encountered and the
        # instruction pointer is within bounds

        while self.running and (self.instruction_ptr < self.memory_len):

            # Get the next opcode and parameter modes from memory
            (opcode, param_modes) = self._parse_instruction(self.memory[self.instruction_ptr])

            # Attempt to resolve the instruction function and length from the opcode dict
            try:
                (instruction, instruction_len) = self.instructions[opcode]
            except KeyError:
                raise RuntimeError(
                    "Invalid opcode {} at instruction pointer {}".format(
                    opcode, self.instruction_ptr
                ))

            # Extract the instruction parameter list from memory
            params = self.memory[self.instruction_ptr+1:self.instruction_ptr+instruction_len]

            if self.diagnostic_debug:
                logging.debug("****: ptr {} mem {} opcode {} params {} param_modes {}".format(
                    self.instruction_ptr, self.memory[self.instruction_ptr], 
                    opcode, params, param_modes
                ))

            # Execute the instruction
            instruction(*params, param_modes)

            # Increment the instruction pointer by the appropriate length
            self.instruction_ptr += instruction_len
            num_instructions += 1

        # Run complete, set the output parameter to the conents of the first memory position
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

    def _extend_memory(self, max_addr):

        required = max_addr - len(self.memory) + 1
        if self.diagnostic_debug:
            logging.debug("****: Extending memory from {} by {} to {}".format(
                len(self.memory), required, max_addr+1
            ))
        self.memory.extend([0] * required)

    def _resolve_params(self, params, param_modes):
        
        if len(params) > len(param_modes):
            raise RuntimeError("Attempting to resolve too many parameters")

        def resolve(param, mode):

            mem_addr = 0
            if mode == self.ParamMode.POSITION:
                mem_addr = param
            elif mode == self.ParamMode.IMMEDIATE:
                return param
            elif mode == self.ParamMode.RELATIVE:
                mem_addr = param + self.relative_base
            else:
                raise RuntimeError("Illegal parameter mode {} encountered".format(mode))

            if mem_addr < 0:
                raise RuntimeError("Attempted to access memory below address 0")

            if mem_addr >= len(self.memory):
                self._extend_memory(mem_addr)

            return self.memory[mem_addr]

        return list(map(resolve, params, param_modes))

    def _resolve_output(self, output, param_modes):

        if param_modes[-1] == self.ParamMode.RELATIVE:
            output = output + self.relative_base
        else:
            output = output 

        if output >= len(self.memory):
            self._extend_memory(output)

        return output

    def _add(self, input_1, input_2, output, param_modes):

        self._operator(input_1, input_2, output, param_modes, operator.add)

    def _multiply(self, input_1, input_2, output, param_modes):

        self._operator(input_1, input_2, output, param_modes, operator.mul)

    def _less_than(self, input_1, input_2, output, param_modes):

        self._operator(input_1, input_2, output, param_modes, operator.lt)

    def _equals(self, input_1, input_2, output, param_modes):

        self._operator(input_1, input_2, output, param_modes, operator.eq)

    def _operator(self, input_1, input_2, output, param_modes, operation):

        (value_1, value_2) = self._resolve_params((input_1, input_2), param_modes)
        output = self._resolve_output(output, param_modes)
        self.memory[output] = int(operation(value_1,value_2))
        
        op_symbol = self.OpSymbols[operation.__name__]
        logging.debug(
            "%s: %04x: %-3s %8x %8x -> %8x", 
            self.name, self.instruction_ptr, 
            operation.__name__.upper(), value_1, value_2, output
        )

    def _input(self, input_ptr, param_modes):

        if self.is_async:
            input_value = self.input_queue.get()
            self.input_queue.task_done()
            logging.debug("Processor {} input value {}".format(self.name, input_value))
        elif self.input_method:
            input_value = self.input_method()
        else:
            input_value = self.inputs.pop(0)

        input_ptr = self._resolve_output(input_ptr, [param_modes[0]])

        logging.debug("%s: %04x: INP %8s %8x -> %8x", 
            self.name, self.instruction_ptr, "[INPUT]", input_value, input_ptr)

        self.memory[input_ptr] = input_value

    def _output(self, output_param, param_modes):
        
        output_value = self._resolve_params([output_param], param_modes)[0]
        logging.debug("%s: %04x: OUT %8x %8s -> %8s", 
            self.name, self.instruction_ptr, output_value, " ", "[OUTPUT]")

        if self.is_async:
            self.output_queue.put(output_value)
            logging.debug("Processor {} output value {}".format(self.name, output_value))
        elif self.output_method:
            self.output_method(output_value)
        else:
            self.outputs.append(output_value)

    def _jump_true(self, input_val, input_jump, param_modes):
        
        self._jump_condition(input_val, input_jump, param_modes, True)

    def _jump_false(self, input_val, input_jump, param_modes):

        self._jump_condition(input_val, input_jump, param_modes, False)

    def _jump_condition(self, input_val, input_jump, param_modes, condition):

        (value, jump_ptr) = self._resolve_params((input_val, input_jump), param_modes)
        cond_str = "JNE" if condition else "JEQ"

        logging.debug("%s: %04x: %-3s %8x %8s -> %8x", 
            self.name, self.instruction_ptr, cond_str, value, "", jump_ptr)

        if (value != 0) == condition:             
            self.instruction_ptr = jump_ptr - 3

    def _adjust_relative(self, adj_param, param_modes):

        adjust_relative = self._resolve_params([adj_param], param_modes)[0]

        logging.debug("%s: %04x: ADJ %8x %8x -> %08x", 
            self.name, self.instruction_ptr, self.relative_base, adjust_relative,
            self.relative_base + adjust_relative)

        self.relative_base += adjust_relative

    def _halt(self, param_modes):
        logging.debug("%s: %04x: HALT", self.name, self.instruction_ptr)
        self.running = False

    def run_self_test_cases(self, name, test_cases, test_results=[], test_inputs=[], test_outputs=[]):

        if len(test_results) == 0:
            test_results = [[]]*len(test_cases)
        if len(test_inputs) == 0:
            test_inputs = [[]]*len(test_cases)
        if len(test_outputs) == 0:
            test_outputs = [[]]*len(test_cases)

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

        logging.info("{} test cases completed OK".format(name))

    def self_test_basic(self):

        test_cases = [
            [1,5,6,3,99,30,40],
            [1,9,10,3,2,3,11,0,99,30,40,50],
            [1,0,0,0,99] ,
            [2,3,0,3,99],
            [2,4,4,5,99,0],
            [1,1,1,4,99,5,6,0,99]
        ]

        test_results = [
            [1,5,6,70,99,30,40],
            [3500,9,10,70,2,3,11,0,99,30,40,50],
            [2,0,0,0,99],
            [2,3,0,6,99],
            [2,4,4,5,99,9801],
            [30,1,1,4,2,5,6,0,99]
        ]

        self.run_self_test_cases('Basic', test_cases, test_results)

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
        self.run_self_test_cases('Part 1', test_cases, test_results, test_inputs, test_outputs)

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
            [178],
            [0],
            [179],
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
            [3, 12, 6, 12, 15, 1, 13, 14, 13, 4, 13, 99, 178, 1, 1, 9],
            [3, 3, 1105, 0, 9, 1101, 0, 0, 12, 4, 12, 99, 0],
            [3, 3, 1105, 179, 9, 1101, 0, 0, 12, 4, 12, 99, 1],
        ]
        self.run_self_test_cases('Part 2a', test_cases, test_results, test_inputs, test_outputs)

        test_cases = [[
            3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
            1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
            999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99
        ]]*3
        test_inputs = [[7], [8], [9]]

        test_outputs = [[999], [1000], [1001]]

        test_results = [
            [
                3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
                1106,0,36,98,0,7,1002,21,125,20,4,20,1105,1,46,104,
                999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99
            ],
            [
                3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
                1106,0,36,98,1000,8,1002,21,125,20,4,20,1105,1,46,104,
                999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99
            ],
            [
                3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
                1106,0,36,98,1001,9,1002,21,125,20,4,20,1105,1,46,104,
                999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99
            ]
        ]
        self.run_self_test_cases('Part 2b', test_cases, test_results, test_inputs, test_outputs)

def run_part_with_inputs(proc, inputs):

    proc.reset_memory()
    proc.load_inputs(inputs)
    proc.run()
    return proc.get_outputs()

def part1(proc):

    proc.reset_memory()

    outputs = run_part_with_inputs(proc, [1])
    outcome = "PASSED" if sum(outputs[:-1]) == 0 else "FAILED"
    logging.info("Part 1: TEST diagnostic {} with code {}".format(
        outcome, outputs[-1]
    ))

def part2(proc):
    
    proc.reset_memory()
    
    outputs = run_part_with_inputs(proc, [5])
    outcome = "PASSED" if len(outputs) == 1 else "FAILED"
    logging.info("Part 2: TEST diagnostic {} with code {}".format(
        outcome, outputs[0]
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

    proc = IntCodeProcessor()
    proc.self_test_basic()
    proc.self_test_part1()
    proc.self_test_part2()

    proc.load_file('input_5.txt')
    part1(proc)
    part2(proc)


if __name__ == '__main__':
    main()