# AOC day 20

import logging
import sys

from collections import defaultdict, deque
import networkx as nx

class PlutoMaze():

    def __init__(self):

        self.maze = defaultdict(lambda: ' ')
        self.rows = 0
        self.cols = 0
        self.start = None
        self.end = None
        self.portal_pos = {}
        self.portal_other = {}
        self.seen = {}

        self.adjacents = [(0,-1), (0,1), (-1,0), (1,0)]

    def load_file(self, file_name):

        with open(file_name) as f:
            input_data = f.readlines()
            self.load_input(input_data)

    def load_input(self, input_data):

        self.rows = len(input_data)
        self.cols = -1
    
        for y, line in enumerate(input_data):
            line = line.rstrip('\n')
            if len(line) > self.cols: self.cols = len(line)
            for x, elem in enumerate(line):
                self.maze[(x,y)] = elem

        self.display_maze()

    def parse_graph_flat(self):

        portals = defaultdict(list)

        def neighbours(x, y):
            adjacents = [(0,-1), (0,1), (-1,0), (1,0)]
            return [(x + dx, y + dy) for dx, dy in adjacents]
            
        self.graph = nx.Graph()
        for y in range(2, self.rows - 2):
            for x in range(2, self.cols - 2):

                if self.maze[(x,y)] != '.':
                    continue
                
                # Add visitable points in maze to graph as nodes
                self.graph.add_node((x, y))

                # Find visitable neighbours and add to graph as edges
                for nb in [(a, b) for a, b in neighbours(x, y) if self.maze[(a, b)] == '.']:
                    self.graph.add_edge((x, y), nb)

                for (dx1, dx2, dy1, dy2) in [
                    (0, 0, -2, -1), 
                    (0, 0, 1, 2),
                    (-2, -1, 0, 0),
                    (1, 2, 0, 0),
                ]:
                    pair = ''.join(sorted(self.maze[(x+dx1, y+dy1)] + self.maze[(x+dx2, y+dy2)]))

                    if pair.isalpha():
                        if pair == 'AA':
                            logging.debug(f"Got start {pair} at ({x},{y})")
                            self.start = (x, y)
                        elif pair == 'ZZ':
                            logging.debug(f"Got end {pair} at ({x},{y})")
                            self.end = (x, y)
                        else:
                            logging.debug(f"Got portal {pair} at ({x},{y})")
                            portals[pair].append((x, y))

        for portal, points in portals.items():
            if len(points) != 2:
                raise RuntimeError(f'Portal {portal} has wrong number of endpoints: {len(points)}')
            logging.debug(f"Adding portal {portal} as graph edge for points {points}")
        
            self.graph.add_edge(points[0], points[1])

        if not self.start:
            raise RuntimeError("No start position found in maze")

        if not self.end:
            raise RuntimeError("No end position found in maze")

        logging.debug(
            "Loaded maze of size {} x {} with {} portals".format(
                self.rows, self.cols, len(portals)
            )
        )


    def parse_graph_levels(self):

        levels = 30
        portals = defaultdict(list)

        def neighbours(x, y):
            adjacents = [(0,-1), (0,1), (-1,0), (1,0)]
            return [(x + dx, y + dy) for dx, dy in adjacents]
            
        self.graph = nx.Graph()
        for y in range(1, self.rows - 1):
            for x in range(1, self.cols - 1):

                if self.maze[(x,y)] != '.':
                    continue
                
                # Add visitable points in maze to graph as nodes
                for i in range(levels):
                    self.graph.add_node((x, y, i))

                # Find visitable neighbours and add to graph as edges
                for nb in [(a, b) for a, b in neighbours(x, y) if self.maze[(a, b)] == '.']:
                    for i in range(levels):
                        self.graph.add_edge((x, y, i), (*nb, i))

                for (dx1, dx2, dy1, dy2) in [
                    (0, 0, -2, -1), 
                    (0, 0, 1, 2),
                    (-2, -1, 0, 0),
                    (1, 2, 0, 0),
                ]:
                    pair = ''.join(sorted(self.maze[(x+dx1, y+dy1)] + self.maze[(x+dx2, y+dy2)]))

                    if pair.isalpha():
                        if pair == 'AA':
                            logging.debug(f"Got start {pair} at ({x},{y})")
                            self.start = (x, y, 0)
                        elif pair == 'ZZ':
                            logging.debug(f"Got end {pair} at ({x},{y})")
                            self.end = (x, y, 0)
                        else:
                            logging.debug(f"Got portal {pair} at ({x},{y})")
                            portals[pair].append((x, y))


        for points in portals.values():
            if len(points) == 2:
                if points[0][0] in [2, self.cols -3] or points[0][1] in [2, self.rows - 3]:
                    outer, inner = points
                else:
                    inner, outer = points
                for i in range(levels):
                    self.graph.add_edge((*inner, i), (*outer, i + 1))
                    self.graph.add_edge((*outer, i + 1), (*inner, i))

        if not self.start:
            raise RuntimeError("No start position found in maze")

        if not self.end:
            raise RuntimeError("No end position found in maze")

        logging.debug(
            "Loaded maze of size {} x {} with {} portals".format(
                self.rows, self.cols, len(portals)
            )
        )

    def display_maze(self):

        logging.debug('   : {}'.format(
            ''.join([str(x//100) for x in range(self.cols)])
        ))
        logging.debug('   : {}'.format(
            ''.join([str((x%100)//10) for x in range(self.cols)])
        ))
        logging.debug('   : {}'.format(
            ''.join([str(x%10) for x in range(self.cols)])
        ))
        for y in range(self.rows):
            line = ''.join([self.maze[x,y] for x in range(self.cols)])
            logging.debug(f"{y:02d} : {line}")


    def find_shortest_path(self):

        return nx.shortest_path_length(self.graph, self.start, self.end)

def test_part1(maze):
    
    test_mazes = [
        [
            '         A           ',
            '         A           ',
            '  #######.#########  ',
            '  #######.........#  ',
            '  #######.#######.#  ',
            '  #######.#######.#  ',
            '  #######.#######.#  ',
            '  #####  B    ###.#  ',
            'BC...##  C    ###.#  ',
            '  ##.##       ###.#  ',
            '  ##...DE  F  ###.#  ',
            '  #####    G  ###.#  ',
            '  #########.#####.#  ',
            'DE..#######...###.#  ',
            '  #.#########.###.#  ',
            'FG..#########.....#  ',
            '  ###########.#####  ',
            '             Z       ',
            '             Z       ',
        ],
        [
            '                   A               ',
            '                   A               ',
            '  #################.#############  ',
            '  #.#...#...................#.#.#  ',
            '  #.#.#.###.###.###.#########.#.#  ',
            '  #.#.#.......#...#.....#.#.#...#  ',
            '  #.#########.###.#####.#.#.###.#  ',
            '  #.............#.#.....#.......#  ',
            '  ###.###########.###.#####.#.#.#  ',
            '  #.....#        A   C    #.#.#.#  ',
            '  #######        S   P    #####.#  ',
            '  #.#...#                 #......VT',
            '  #.#.#.#                 #.#####  ',
            '  #...#.#               YN....#.#  ',
            '  #.###.#                 #####.#  ',
            'DI....#.#                 #.....#  ',
            '  #####.#                 #.###.#  ',
            'ZZ......#               QG....#..AS',
            '  ###.###                 #######  ',
            'JO..#.#.#                 #.....#  ',
            '  #.#.#.#                 ###.#.#  ',
            '  #...#..DI             BU....#..LF',
            '  #####.#                 #.#####  ',
            'YN......#               VT..#....QG',
            '  #.###.#                 #.###.#  ',
            '  #.#...#                 #.....#  ',
            '  ###.###    J L     J    #.#.###  ',
            '  #.....#    O F     P    #.#...#  ',
            '  #.###.#####.#.#####.#####.###.#  ',
            '  #...#.#.#...#.....#.....#.#...#  ',
            '  #.#####.###.###.#.#.#########.#  ',
            '  #...#.#.....#...#.#.#.#.....#.#  ',
            '  #.###.#####.###.###.#.#.#######  ',
            '  #.#.........#...#.............#  ',
            '  #########.###.###.#############  ',
            '           B   J   C               ',
            '           U   P   P               ',
        ],
    ]

    test_shortest_paths = [
        23, 58
    ]

    for (test_maze, test_shortest_path) in zip(test_mazes, test_shortest_paths):

        maze.load_input(test_maze)
        maze.parse_graph_flat()
        shortest_path = maze.find_shortest_path()
        assert test_shortest_path == shortest_path

    logging.info("Part 1: tests completed OK")

def test_part2(maze):

    test_mazes = [
        [
            '             Z L X W       C                 ',
            '             Z P Q B       K                 ',
            '  ###########.#.#.#.#######.###############  ',
            '  #...#.......#.#.......#.#.......#.#.#...#  ',
            '  ###.#.#.#.#.#.#.#.###.#.#.#######.#.#.###  ',
            '  #.#...#.#.#...#.#.#...#...#...#.#.......#  ',
            '  #.###.#######.###.###.#.###.###.#.#######  ',
            '  #...#.......#.#...#...#.............#...#  ',
            '  #.#########.#######.#.#######.#######.###  ',
            '  #...#.#    F       R I       Z    #.#.#.#  ',
            '  #.###.#    D       E C       H    #.#.#.#  ',
            '  #.#...#                           #...#.#  ',
            '  #.###.#                           #.###.#  ',
            '  #.#....OA                       WB..#.#..ZH',
            '  #.###.#                           #.#.#.#  ',
            'CJ......#                           #.....#  ',
            '  #######                           #######  ',
            '  #.#....CK                         #......IC',
            '  #.###.#                           #.###.#  ',
            '  #.....#                           #...#.#  ',
            '  ###.###                           #.#.#.#  ',
            'XF....#.#                         RF..#.#.#  ',
            '  #####.#                           #######  ',
            '  #......CJ                       NM..#...#  ',
            '  ###.#.#                           #.###.#  ',
            'RE....#.#                           #......RF',
            '  ###.###        X   X       L      #.#.#.#  ',
            '  #.....#        F   Q       P      #.#.#.#  ',
            '  ###.###########.###.#######.#########.###  ',
            '  #.....#...#.....#.......#...#.....#.#...#  ',
            '  #####.#.###.#######.#######.###.###.#.#.#  ',
            '  #.......#.......#.#.#.#.#...#...#...#.#.#  ',
            '  #####.###.#####.#.#.#.#.###.###.#.###.###  ',
            '  #.......#.....#.#...#...............#...#  ',
            '  #############.#.#.###.###################  ',
            '               A O F   N                     ',
            '               A A D   M                     ',
        ],
    ]

    test_shortest_paths = [
        396
    ]
    for (test_maze, test_shortest_path) in zip(test_mazes, test_shortest_paths):

        maze.load_input(test_maze)
        maze.parse_graph_levels()
        shortest_path = maze.find_shortest_path()
        assert test_shortest_path == shortest_path

    logging.info("Part 2: tests completed OK")

def part1(maze):
    
    maze.load_file('input/input_20.txt')
    maze.parse_graph_flat()
    shortest_path = maze.find_shortest_path()
    logging.info(f"Part 1: the shortest path to the end point has length {shortest_path}")

def part2(maze):
    
    maze.load_file('input/input_20.txt')
    maze.parse_graph_levels()
    shortest_path = maze.find_shortest_path()
    logging.info(f"Part 2: the shortest path to the end point has length {shortest_path}")

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

    maze = PlutoMaze()
    
    test_part1(maze)
    test_part2(maze)

    part1(maze)
    part2(maze)

if __name__ == '__main__':
    main()