# AOC Day 3

import logging

class Wire(object):

    def __init__(self, wire_desc):

        self.x = 0
        self.y = 0 

        self.segments = len(wire_desc)
        self.length = 0
        self._points = {}

        for segment in wire_desc:
            direction = segment[0]
            distance = int(segment[1:])
            #logging.debug("Segment {} direction {} distance {}".format(segment, direction, distance))

            for step in range(distance):
                if direction == 'R':
                    self.x += 1
                elif direction == 'L':
                    self.x -= 1
                elif direction == 'U':
                    self.y += 1
                elif direction == 'D':
                    self.y -= 1
                else:
                    raise RuntimeError("Bad direction {} on segment {}".format(direction, segment))
                self.length += 1
                if (self.x, self.y) not in self._points:
                    self._points[(self.x, self.y)] = self.length

        logging.debug("Wire has {} segments, length {} and {} unique points".format(
            self.segments, self.length, len(self._points)
        ))

    def points(self):
        return set(self._points.keys())

    def point_length(self, point):
        return self._points[point]

class FuelManagementSystem(object):

    def __init__(self):

        self.wires = []
        self.intersections = None
        pass

    def load_file(self, file_name):

        self.wires = []
        self.intersections = None

        with open(file_name, 'r') as f:
            lines = f.readlines()

        for line in lines:
            wire_desc = [val for val in line.strip().split(',')]

            self.wires.append(Wire(wire_desc))

    def load_desc(self, wire_descs):

        self.wires = []
        self.intersections = None
        for wire_desc in wire_descs:
            self.wires.append(Wire(wire_desc))

    def find_intersections(self):

        all_points = tuple(wire.points() for wire in self.wires)
        self.intersections = set()

        for wire in self.wires:
            self.intersections.update(wire.points().intersection(*all_points))
                
    def find_closest_intersection(self):

        if self.intersections is None:
            self.find_intersections()

        def manhattan_dist(point):
            (x, y) = point
            return abs(x) + abs(y)

        closest = sorted(self.intersections, key=manhattan_dist)[0]
        min_distance = manhattan_dist(closest)

        logging.debug('System has {} intersections: {}, the closest is {} with Manhattan distance {}'.format(
            len(self.intersections), ' '.join([repr(inter) for inter in self.intersections]),
            repr(closest), min_distance
        ))

        return (closest, min_distance)

    def find_shortest_intersection(self):

        if self.intersections is None:
            self.find_intersections()

        def total_length(intersection):
            total_length = sum([wire.point_length(intersection) for wire in self.wires])
            return total_length

        shortest = sorted(self.intersections, key=total_length)[0]
        min_length = total_length(shortest)    

        logging.debug("Intersection {} has shortest total path length of {}".format(
            repr(shortest), min_length
        ))

        return (shortest, min_length)

    def self_test(self):

        tests = [
            (
                ['R8','U5','L5','D3'], 
                ['U7','R6','D4','L4'], 
                6,
                30
            ),
            (
                ['R75','D30','R83','U83','L12','D49','R71','U7','L72'],
                ['U62','R66','U55','R34','D71','R55','D58','R83'], 
                159,
                610
            ),
            (
                ['R98','U47','R26','D63','R33','U87','L62','D20','R33','U53','R51'],
                ['U98','R91','D20','R16','D67','R40','U7','R15','U6','R7'],
                135,
                410
            )
        ]
        for test in tests:
            wire_descs = (test[0], test[1])
            distance = test[2]
            length = test[3]
            self.load_desc(wire_descs)
            (closest, min_distance) = self.find_closest_intersection()
            (shortest, min_length) = self.find_shortest_intersection()
            assert min_distance == distance
            assert min_length == length

def main():

    logging.basicConfig(
        level=logging.DEBUG, format='%(levelname)-8s: %(message)s', datefmt='%H:%M:%S'
    )

    fms = FuelManagementSystem()
    fms.self_test()

    fms.load_file('input_3.txt')
    (closest, min_distance) = fms.find_closest_intersection()
    logging.info("Part 1 : closest intersection has distance {}".format(min_distance))

    (shortest, min_length) = fms.find_shortest_intersection()
    logging.info("Part 2: shortest intersection has total length {}".format(min_length))

if __name__ == '__main__':

    main()