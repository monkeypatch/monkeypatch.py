import hashlib
import math

import numpy as np
from bitarray import bitarray

from monkey_patch.persistence.filter.bloom_interface import IBloomFilterPersistence


class BloomFilter:

    def __init__(self,
                 persistence: IBloomFilterPersistence,
                 size=None,
                 hash_count=None,
                 expected_number_of_elements=None,
                 false_positive_probability=None):

        if not persistence:
            raise ValueError("Persistence cannot be None, it must be an instance of IBloomFilterPersistence")

        if not size and not hash_count and not expected_number_of_elements and not false_positive_probability:
            raise ValueError("Must specify either (size, hash_count) or (expected_number_of_elements, false_positive_probability")

        if expected_number_of_elements and false_positive_probability:
            size, hash_count = BloomFilter.optimal_bloom_filter_params(expected_number_of_elements, false_positive_probability)

        if not size and not hash_count:
            raise ValueError("Size and hash_count not set. This should never happen.")

        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)
        self.indices = np.zeros(size, dtype=np.int32)
        self.persistence = persistence

    def hash_functions(self, string):
        # h1(x)
        hash1 = int(hashlib.sha256(string.encode('utf-8')).hexdigest(), 16)
        # h2(x)
        hash2 = int(hashlib.md5(string.encode('utf-8')).hexdigest(), 16)
        return hash1, hash2

    def lookup(self, string):
        hash1, hash2 = self.hash_functions(string)
        for seed in range(self.hash_count):
            index = (hash1 + seed * hash2) % self.size

            #print(f"Lookup: Seed={seed}, Digest={index}, BitValue={self.bit_array[index]}")
            if self.bit_array[index] == 0:
                return False
        return True

    def add(self, string):
        hash1, hash2 = self.hash_functions(string)
        for seed in range(self.hash_count):
            index = (hash1 + seed * hash2) % self.size
            self.bit_array[index] = 1
            #print(f"Add: Seed={seed}, Digest={index}, BitValue={self.bit_array[index]}")

    def save(self):
        self.persistence.save(self)

    def load(self):
        return self.persistence.load()

    @staticmethod
    def optimal_bloom_filter_params(n, p):
        """
        Calculate the optimal bit array size (m) and number of hash functions (k)
        for a Bloom filter.

        n: expected number of items to be stored
        p: acceptable false positive probability

        Returns a tuple (m, k)
        """
        m = - (n * math.log(p)) / (math.log(2) ** 2)
        k = (m / n) * math.log(2)
        return int(math.ceil(m)), int(math.ceil(k))