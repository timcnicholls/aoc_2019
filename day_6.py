# AOC Day 6

import logging
import sys

class UniversalOrbitMap(object):

    def __init__(self, orbit_map=None):

        self.bodies = {}

        if orbit_map:
            self.parse_map(orbit_map)

    def load_file(self, file_name):

        with open(file_name, 'r') as f:
            orbit_map = f.readlines()
        self.parse_map(orbit_map)

    def parse_map(self, orbit_map):

        self.bodies = {}

        for orbit in orbit_map:
            (parent, body) = orbit.strip().split(')')
            if body in parent:
                logging.warning("Body {} already exists in map with parent {}".format(
                    body, self.bodies[body]
                ))
            self.bodies[body] = parent

        logging.debug("Parsed orbit map of length {} containing {} objects".format(
            len(orbit_map), len(self.bodies)
        ))

    def calculate_orbits(self):
        
        total_orbits = 0
        for body in self.bodies:
            while body in self.bodies:
                total_orbits += 1
                body = self.bodies[body]

        logging.debug("Total number of orbits : {}".format(total_orbits))
        return total_orbits

    def get_path(self, body):

        path = []
        while body in self.bodies:
            path.append(body)
            body = self.bodies[body]

        return path

    def calculate_transfer(self, body_1, body_2):

        path_elems_1 = set(self.get_path(body_1))
        path_elems_2 = set(self.get_path(body_2))

        transfer = len(path_elems_1.symmetric_difference(path_elems_2)) - 2
        
        return transfer

    def self_test_part1(self):

        logging.info("Running UOM self test part 1")
        test_map = [
            "COM)B",
            "B)C",
            "C)D",
            "D)E",
            "E)F",
            "B)G",
            "G)H",
            "D)I",
            "E)J",
            "J)K",
            "K)L",
        ]
        test_num_orbits = 42

        self.parse_map(test_map)
        num_orbits = self.calculate_orbits()
        assert test_num_orbits == num_orbits

    def self_test_part2(self):
        
        logging.info("Running UOM self test part 2")
        test_map = [
            "COM)B",
            "B)C",
            "C)D",
            "D)E",
            "E)F",
            "B)G",
            "G)H",
            "D)I",
            "E)J",
            "J)K",
            "K)L",
            "K)YOU",
            "I)SAN",
        ]

        test_transfer = 4
        self.parse_map(test_map)
        num_orbits = self.calculate_orbits()

        transfer = self.calculate_transfer("YOU", "SAN")
        assert test_transfer == transfer

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

    uom = UniversalOrbitMap()
    uom.self_test_part1()
    uom.self_test_part2()

    uom.load_file('input_6.txt')
    total_orbits = uom.calculate_orbits()
    logging.info("Part 1: total number of orbits: {}".format(total_orbits))

    transfer_len = uom.calculate_transfer("YOU", "SAN")
    logging.info("Part 2: orbital transfer length = {}".format(transfer_len))

if __name__ == '__main__':
    main()