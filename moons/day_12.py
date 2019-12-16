
# AOC Day 12

import itertools
import logging
import sys

class Moon(object):
    
    num_coords = 3

    def __init__(self, position=[0,0,0], id=None):

        self.initial_position = list(position)
        self.position = list(position)
        self.id = id

        self.velocity = [0, 0, 0]

    def total_energy(self):

        potential = sum([abs(pos) for pos in self.position])
        kinetic = sum([abs(vel) for vel in self.velocity])

        total_energy = potential * kinetic

        return total_energy

    def __repr__(self):
        return '{} : pos=<x={:-3d} y={:-3d} z={:-3d}> vel=<x={:-3d} y={:-3d} z={:-3d}>'.format(
            self.id,
            self.position[0], self.position[1], self.position[2],
            self.velocity[0], self.velocity[1], self.velocity[2]
        )

class MoonSystem(object):

    def __init__(self):

        self.moons = []

    def load_file(self, file_name):

        with open(file_name, 'r') as f:
            moon_data = f.readlines()
            self.load_moons(moon_data)

    def load_moons(self, moon_data):

        self.moons = []
        for line in moon_data:
            position = [int(elem.split('=')[1]) for elem in line.strip()[1:-1].split(',')]
            self.moons.append(Moon(position, len(self.moons)))

    def show_state(self):

        for (idx, moon) in enumerate(self.moons):
            logging.debug('Moon {} : {}'.format(idx, moon))

    def evolve_state(self, num_steps=1):

        for _ in range(num_steps):
            # Apply gravity to update velocity
            for (a, b) in itertools.combinations(self.moons, 2):
                for i_coord in range(Moon.num_coords):
                    if a.position[i_coord] < b.position[i_coord]:
                        delta_v = 1
                    elif a.position[i_coord] > b.position[i_coord]:
                        delta_v = -1
                    else:
                        delta_v = 0
                    a.velocity[i_coord] += delta_v
                    b.velocity[i_coord] -= delta_v

            # Update positions using velocity
            for moon in self.moons:
                for i_coord in range(Moon.num_coords):
                    moon.position[i_coord] += moon.velocity[i_coord]

    def total_energy(self):

        total_energy = sum([moon.total_energy() for moon in self.moons])

        return(total_energy)

    def find_first_repeat(self):

        cycles = [None] * Moon.num_coords
        step = 0

        with open('moons.txt', 'w+') as f:

            f.write('{} {}\n'.format(
                step, ' '.join(['{} {}'.format(
                    moon.position[0], moon.velocity[0]) for moon in self.moons]
                )
            ))

            while not all(cycles):

                self.evolve_state()
                step += 1
                f.write('{} {}\n'.format(
                    step, ' '.join(['{} {}'.format(
                        moon.position[0], moon.velocity[0]) for moon in self.moons]
                    )
                ))
                for i_coord in range(Moon. num_coords):

                    if cycles[i_coord] is not None:
                        continue

                    for moon in self.moons:
                        if moon.position[i_coord] != moon.initial_position[i_coord]:
                            break
                        if moon.velocity[i_coord] != 0:
                            break
                    else:
                        cycles[i_coord] = step # * 2

        def gcd(a, b):
            while b > 0:
                a, b = b, a % b
            return a

        def lcm(a, b):
            return a * b / gcd(a, b)

        first_repeat = lcm(lcm(cycles[0], cycles[1]), cycles[2])
        logging.debug("Found all cycles {} after {} steps yielding a first repeat of {}".format(
            cycles, step, first_repeat   
        ))

        return first_repeat

def test_part1():
    
    system = MoonSystem()

    test_initial_positions = [
        [
            '<x=-1, y=0, z=2>',
            '<x=2, y=-10, z=-7>',
            '<x=4, y=-8, z=8>',
            '<x=3, y=5, z=-1>',
        ],
        [
            '<x=-8, y=-10, z=0>',
            '<x=5, y=5, z=10>',
            '<x=2, y=-7, z=3>',
            '<x=9, y=-8, z=-3>',
        ]
    ]
    test_num_steps = [10, 100]
    test_total_energies= [179, 1940]

    for (test_initial_position, num_steps, test_total_energy) in zip(
        test_initial_positions, test_num_steps, test_total_energies
    ):

        system.load_moons(test_initial_position)

        logging.debug("Inital state:")
        system.show_state()

        system.evolve_state(num_steps)

        logging.debug("After {} steps, moons are in state:".format(num_steps))
        system.show_state()

        total_energy = system.total_energy()
        logging.debug("Total energy of system: {}".format(total_energy))
        assert test_total_energy == total_energy

    logging.debug("Part 1: tests completed OK")

def part1():

    system = MoonSystem()
    system.load_file('input_12.txt')
    
    num_steps = 1000
    system.evolve_state(num_steps)
    total_energy = system.total_energy()
    logging.info("Part 1: after {} steps, the system has total energy {}".format(
        num_steps, total_energy
    ))


def test_part2():

    system = MoonSystem()

    test_initial_positions = [
        [
            '<x=-1, y=0, z=2>',
            '<x=2, y=-10, z=-7>',
            '<x=4, y=-8, z=8>',
            '<x=3, y=5, z=-1>',
        ],
        [
            '<x=-8, y=-10, z=0>',
            '<x=5, y=5, z=10>',
            '<x=2, y=-7, z=3>',
            '<x=9, y=-8, z=-3>',
        ]
    ]
    test_first_repeats = [
        2772, 4686774924
    ]

    for (test_initial_position, test_first_repeat) in zip(
        test_initial_positions, test_first_repeats
    ):
        system.load_moons(test_initial_position)
        first_repeat = system.find_first_repeat()
        logging.debug("System has first repeat after {} steps".format(first_repeat))
        assert test_first_repeat == first_repeat
        logging.debug("Part 2: tests completed OK")


def part2():
    
    system = MoonSystem()
    system.load_file('input_12.txt')
    first_repeat = system.find_first_repeat()
    logging.info("Part 2: system repeats after {} steps".format(first_repeat))

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