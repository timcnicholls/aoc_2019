import logging
import sys

import numpy as np

# import numpy as np
# digits = [int(i) for i in open('input.txt', 'r').read().strip()]

# layers = np.array(digits).reshape((-1,6,25))
# composite = np.apply_along_axis(lambda x: x[np.where(x != 2)[0][0]], axis=0, arr=layers)

# print("Part 2:")
# print("\n".join(''.join(u" ♥️"[int(i)] for i in line) for line in composite))

class SIFDecoder(object):

    def __init__(self, width, height):

        self.width = width
        self.height = height
        self.layer_size = width * height
        self.image = None
        self.num_layers = 0

    def load_file(self, file_name):

        sif_data = []
        with open(file_name, 'r') as f:
            sif_data.extend(f.read().strip())

        self.load_data(sif_data)

    def load_data(self, sif_data):

        self.image = np.array([int(x) for x in sif_data])
        self.image = self.image.reshape(-1, self.layer_size)

        assert len(sif_data) % (self.layer_size) == 0
        self.num_layers = len(sif_data) // self.layer_size

        logging.debug("Loaded SIF file of size {} with {} layers".format(
            self.image.size, self.num_layers
        ))

    def find_minzero_product(self):

        idx = (self.image != 0).sum(axis=1).argmax()
        product = (self.image[idx] == 1).sum() * (self.image[idx] == 2).sum()

        return product

    def decode_image(self):
        
        decoded = np.apply_along_axis(
            lambda x: x[np.where(x != 2)[0][0]], axis=0, arr=self.image
        )

        return decoded.reshape(self.height, self.width)

def part1(decoder):

    product = decoder.find_minzero_product()
    logging.info("Part 1: Ones-twos product for minimum zero layer is {}".format(product))

def test_part2():

    decoder = SIFDecoder(2, 2)
    sif_data = [int(char) for char in '0222112222120000']
    decoder.load_data(sif_data)
    decoded = decoder.decode_image()
    assert np.array_equal(decoded, np.array([[0,1],[1,0]]))

def part2(decoder):
    
    decoded = decoder.decode_image()
    logging.info("Part 2 ouput:\n{}".format(
        "\n".join(''.join(u" *"[int(i)] for i in line) for line in decoded)
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

    width = 25
    height = 6
    decoder = SIFDecoder(width, height)
    decoder.load_file('input_8.txt')

    part1(decoder)
    test_part2()
    part2(decoder)

if __name__ == '__main__':
    main()