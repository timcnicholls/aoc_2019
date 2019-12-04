
# AOC day 1

# Fuel calculation for part 1
def calc_fuel(mass):

    fuel = (mass // 3) -2
    return fuel

# Test cases for part 1 calculation
assert 654 == calc_fuel(1969)
assert 33583 == calc_fuel(100756)

# Fuel calculation for part 2
def calc_fuel_full(mass):

    full_fuel = 0
    fuel = calc_fuel(mass)

    while fuel > 0:
        full_fuel += fuel
        fuel = calc_fuel(fuel)
    
    return full_fuel

# Test cases for part 2
assert 966 == calc_fuel_full(1969)
assert 50346 == calc_fuel_full(100756)

# Read in input data and convert to list of ints
with open('input_1.txt', 'r') as f:
    module_txt = f.readlines()
module_mass = [int(mass.strip()) for mass in module_txt]

# Part 1 calculation
total_fuel = sum([calc_fuel(mass) for mass in module_mass])
print("Part 1: total fuel required is {}".format(total_fuel))

# Part 2 calculation
total_full_fuel = sum([calc_fuel_full(mass) for mass in module_mass])
print("Part 2: total fuel required is {}".format(total_full_fuel))
