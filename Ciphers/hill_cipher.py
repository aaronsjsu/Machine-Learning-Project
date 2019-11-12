"""
This file is used to implement the hill cipher. It works by reading input from a
specified txt file at a random line in the file, filtering the characters to be
lowercase letters (discarding non-letter characters), and then encrypting using a
random matrix (of size 2x2, 5x5, or 10x10) as the key. The key is randomized. For
details on how the hill cipher works, see https://en.wikipedia.org/wiki/Hill_cipher.

The result is written to a txt file at the specified location. Uses multiprocessing
to run multiple instances of the cipher in parallel. That way large amounts of data
can be processed at a time, outputting to multiple files in order to get large
variations in the data.


__author__ = "Aaron Smith"
__date__ = "11/10/2019"
"""

import random
import string
import numpy as np
from multiprocessing import Process
from collections import OrderedDict
from math import gcd


# This function makes a random key (a key is a matrix in the hill cipher).
def randomize_matrix(key, key_size, key_phrase):
    for j in range(key_size):
        row = []
        for k in range(key_size):
            val = random.randint(0, 25)
            row.append(val)
            key_phrase += str(val) + " "
        key.append(row)
    return [key, key_phrase]


def make_file(length):
    input_file_name = "brown_corpus.txt"
    output_file_name = "../Data/Hill Cipher/text_length_" + str(length) + ".txt"
    text_length = length # Length of the character sequence to encrypt
    iters = 10000 # How many times to encrypt a string (different string each time)

    file_output = open(output_file_name, "w")

    for i in range(iters):
        # Our key (in the form of a matrix) will be NxN where N = key_size. The size has to be
        # divisible by text_length. Thus, we use 2, 5 or 10.
        key_size = random.choice([2, 5, 10])
        # Now fill our key matrix with random values between 0 and 25. Make sure it's invertible by
        # checking that the determinant isn't equal to 0. numpy is used to find determinant. Also,
        # the determinant must be coprime with 26 (number of letters). Keep attempting to make a matrix
        # until one is found
        key_phrase = ""
        [key, key_phrase] = randomize_matrix([], key_size, key_phrase)
        determinant = np.linalg.det(np.array(key))
        while int(round(determinant)) == 0 or int(gcd(int(round(determinant)), 26)) != 1:
            # If key doesn't work, recompute it, as well as its determinant.
            [key, key_phrase] = randomize_matrix([], key_size, key_phrase)
            determinant = np.linalg.det(np.array(key))

        result = "" # Store the result in this string
        file_input = open(input_file_name, "r")

        # Start our reading from a relatively random line from within the input file.
        random_line = random.randint(1, 45000)
        for j in range(random_line):
            file_input.readline()

        plaintext_vector = []

        # Read plaintext line by line. Break once result string is desired length.
        while (len(result) != text_length):
            line = file_input.readline()
            for char in line:
                if char.isalpha(): # True if char is a letter (i.e. no special characters, no spaces, etc.)
                    plaintext_vector.append(ord(char.lower()) - 97)
                    if len(plaintext_vector) == key_size:
                        result_vector = [0 for j in range(key_size)]
                        # Now multiply the key by the plaintext vector. Results should be in the range 0-25.
                        for j in range(key_size):
                            for k in range(key_size):
                                result_vector[j] += key[j][k] * plaintext_vector[k]
                            result_vector[j] %= 26
                        # Store the result.
                        for val in result_vector:
                            result += chr(val + 97)
                        plaintext_vector = []
                    if len(result) == text_length:
                        break

        # Write result to our output file
        file_output.write(result + " key: " + str(key_phrase) + ", reading from line " + str(random_line) + "\n")
        file_input.close()

    file_output.close()


# Make our program run multiple instances in parallel
processes = []
text_lengths = [100, 200, 300, 500, 1000]
for length in text_lengths:
    print("Starting on length: " + str(length))
    process = Process(target = make_file, args = (length,))
    process.start()
    processes.append(process)

# Wait for processes to finish
for process in processes:
    process.join()

print("done")
