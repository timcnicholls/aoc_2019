# AOC Day 4

import functools
import itertools
import logging
import re

def find_matching(min_val, max_val, reject_longer=False):

    def matches(val):

        val_str = str(val)

        if not len(val_str) == 6:
            return False

        repeats = [''.join(g) for k, g in itertools.groupby(val_str)]
        if not any([len(repeat) > 1 for repeat in repeats]):
            return False

        if reject_longer:
            has_doubles = any([len(repeat) == 2 for repeat in repeats])
            has_longer  = any([len(repeat) > 2 for repeat in repeats])

            if has_longer and not has_doubles:
                return False

        for idx in range(len(val_str)-1):
            if int(val_str[idx]) > int(val_str[idx+1]):
                return False

        return True

    return sum(map(matches, (val for val in range(min_val, max_val+1))))

def test():

    for (val, desired) in [
        (123456, False),
        (112345, True),
        (122345, True),
        (123466, True),
        (112365, False),
        (111111, False),
        (223450, False),
        (123789, False),
        (112233, True),
        (123444, False),
        (111122, True),
    ]:
        result = bool(find_matching(val, val, True))
        logging.debug("Value: {} : {}".format(val, result))
        assert desired == result

def main():

    logging.basicConfig(
        level=logging.INFO, format='%(levelname)-8s: %(message)s', datefmt='%H:%M:%S'
    )

    test()
    min_val = 109165
    max_val = 576723
    logging.info("Part 1 : number of matching passwords is {}".format(
        find_matching(min_val,max_val, False)
    ))
    logging.info("Part 2 : number of matching passwords is {}".format(
        find_matching(min_val,max_val, True)
    ))

if __name__ == '__main__':
    main()