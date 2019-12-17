# AOC day 14

import logging
import math
import sys

from collections import defaultdict

class NanoFactory():

    def __init__(self):

        self.reactions = {}

    def load_file(self, file_name):

        input_data = []
        with open(file_name) as f:
            self.load_input([line.strip() for line in f.readlines()])

    def load_input(self, input_data):

        def _parse_entry(entry):
            quantity, chemical = entry.strip().split()
            return int(quantity), chemical

        self.reactions = {}
        for line in input_data:
            (reactant_txt, product_txt) = line.split('=>')
            (qty, product) = _parse_entry(product_txt)
            self.reactions[product] = (
                qty, list(map(_parse_entry, reactant_txt.strip().split(',')))
            )
        
        logging.debug("Parsed {} reactions from input data".format(len(self.reactions)))


    def calc_ore(self, fuel):

        need = defaultdict(int, {'FUEL': fuel})

        while True:
            try:
                chemical, qty = next(
                    (chem,qty) for chem,qty in need.items() if qty > 0 and chem != 'ORE'
                )
            except: 
                break

            prod_qty, reactants = self.reactions[chemical]
            qty_scale = math.ceil(qty / prod_qty)

            for coef,reactant in reactants:
                need[reactant] += qty_scale * coef

            need[chemical] -= qty_scale * prod_qty

        return need['ORE']

    def calc_fuel(self, ore):

        min_fuel = ore // self.calc_ore(1)
        max_fuel = 2 * min_fuel

        while max_fuel > min_fuel + 1:
            prod_fuel = min_fuel + (max_fuel - min_fuel) // 2

            logging.debug("[{}, {}]: {}".format(max_fuel, min_fuel, prod_fuel))
            if self.calc_ore(prod_fuel) > ore:
                max_fuel = prod_fuel
            else:
                min_fuel = prod_fuel

        return min_fuel

def test_part1(nano):
    
    test_reactions = [
        [
            '10 ORE => 10 A',
            '1 ORE => 1 B',
            '7 A, 1 B => 1 C',
            '7 A, 1 C => 1 D',
            '7 A, 1 D => 1 E',
            '7 A, 1 E => 1 FUEL',
        ],
        [
            '9 ORE => 2 A',
            '8 ORE => 3 B',
            '7 ORE => 5 C',
            '3 A, 4 B => 1 AB',
            '5 B, 7 C => 1 BC',
            '4 C, 1 A => 1 CA',
            '2 AB, 3 BC, 4 CA => 1 FUEL',
        ],
        [
            '157 ORE => 5 NZVS',
            '165 ORE => 6 DCFZ',
            '44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL',
            '12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ',
            '179 ORE => 7 PSHF',
            '177 ORE => 5 HKGWZ',
            '7 DCFZ, 7 PSHF => 2 XJWVT',
            '165 ORE => 2 GPVTF',
            '3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT',
        ],
        [
            '2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG',
            '17 NVRVD, 3 JNWZP => 8 VPVL',
            '53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL',
            '22 VJHF, 37 MNCFX => 5 FWMGM',
            '139 ORE => 4 NVRVD',
            '144 ORE => 7 JNWZP',
            '5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC',
            '5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV',
            '145 ORE => 6 MNCFX',
            '1 NVRVD => 8 CXFTF',
            '1 VJHF, 6 MNCFX => 4 RFSQX',
            '176 ORE => 6 VJHF',
        ],
        [
            '171 ORE => 8 CNZTR',
            '7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL',
            '114 ORE => 4 BHXH',
            '14 VRPVC => 6 BMBT',
            '6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL',
            '6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT',
            '15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW',
            '13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW',
            '5 BMBT => 4 WPTQ',
            '189 ORE => 9 KTJDG',
            '1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP',
            '12 VRPVC, 27 CNZTR => 2 XDBXC',
            '15 KTJDG, 12 BHXH => 5 XCVML',
            '3 BHXH, 2 VRPVC => 7 MZWV',
            '121 ORE => 7 VRPVC',
            '7 XCVML => 6 RJRHP',
            '5 BHXH, 4 VRPVC => 5 LTCX',
        ]
    ]

    test_ore_reqs = [
        31, 165, 13312, 180697, 2210736
    ]

    for (test_reaction, test_ore_required) in zip(test_reactions, test_ore_reqs):

        nano.load_input(test_reaction)
        ore_required = nano.calc_ore(1)
        assert test_ore_required == ore_required

    logging.info("Part 1: tests completed OK")

def test_part2(nano):

    test_reactions = [
        [
            '157 ORE => 5 NZVS',
            '165 ORE => 6 DCFZ',
            '44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL',
            '12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ',
            '179 ORE => 7 PSHF',
            '177 ORE => 5 HKGWZ',
            '7 DCFZ, 7 PSHF => 2 XJWVT',
            '165 ORE => 2 GPVTF',
            '3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT',
        ],
        [
            '2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG',
            '17 NVRVD, 3 JNWZP => 8 VPVL',
            '53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL',
            '22 VJHF, 37 MNCFX => 5 FWMGM',
            '139 ORE => 4 NVRVD',
            '144 ORE => 7 JNWZP',
            '5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC',
            '5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV',
            '145 ORE => 6 MNCFX',
            '1 NVRVD => 8 CXFTF',
            '1 VJHF, 6 MNCFX => 4 RFSQX',
            '176 ORE => 6 VJHF',
        ],
        [
            '171 ORE => 8 CNZTR',
            '7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL',
            '114 ORE => 4 BHXH',
            '14 VRPVC => 6 BMBT',
            '6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL',
            '6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT',
            '15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW',
            '13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW',
            '5 BMBT => 4 WPTQ',
            '189 ORE => 9 KTJDG',
            '1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP',
            '12 VRPVC, 27 CNZTR => 2 XDBXC',
            '15 KTJDG, 12 BHXH => 5 XCVML',
            '3 BHXH, 2 VRPVC => 7 MZWV',
            '121 ORE => 7 VRPVC',
            '7 XCVML => 6 RJRHP',
            '5 BHXH, 4 VRPVC => 5 LTCX',
        ]
    ]

    test_fuel_prods = [
        82892753, 5586022, 460664
    ]

    for (test_reaction, test_fuel_produced) in zip(test_reactions, test_fuel_prods):

        ore = 1000000000000
        nano.load_input(test_reaction)
        fuel_produced = nano.calc_fuel(ore)
        assert test_fuel_produced == fuel_produced

    logging.info("Part 2: tests completed OK")

def part1(nano):
    
    ore_required= nano.calc_ore(1)
    logging.info("Part 1: production of 1 unit of fuel requires {} units of ore".format(
        ore_required
    ))

def part2(nano):
    
    ore = 1000000000000
    fuel_produced = nano.calc_fuel(ore)

    logging.info("Part 2: with {} units of ore, can produce {} units of fuel".format(
        ore, fuel_produced
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

    nano = NanoFactory()
    
    test_part1(nano)
    test_part2(nano)

    nano.load_file('input/input_14.txt')

    part1(nano)
    part2(nano)

if __name__ == '__main__':
    main()