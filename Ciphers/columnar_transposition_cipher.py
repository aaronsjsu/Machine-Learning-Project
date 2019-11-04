"""
This file is used to implement a columnar transposition cipher. It works by reading input
from a specified txt file at a random line, filtering the characters to be lowercase
letters (discarding non-letter characters), and then encrypting the characters using the
columnar transposition cipher. See
http://practicalcryptography.com/ciphers/columnar-transposition-cipher/ for a brief
description of the cipher. Can be editted to use a random key, or a default key.

It writes the result to a txt file at the specified location. Uses multiprocessing
to run multiple instances of the cipher in parallel. That way large amounts of data
can be processed at a time, outputting to multiple files in order to get large
variations in the data.

__author__ = "Aaron Smith"
__date__ = "11/4/2019"
"""

import random
from multiprocessing import Process

def make_file(length):
    input_file_name = "brown_corpus.txt"
    output_file_name = "../Data/Columnar Transposition Cipher/Random Key Random Length/text_length_" + str(length) + ".txt"
    text_length = length # Length of the character sequence to encrypt
    iters = 10000 # How many times to encrypt a string

    file_output = open(output_file_name, "w")

    for j in range(iters):
        # Number of columns for our columnar transposition. Can be 5 or 10 (must go into text_length evenly).
        number_of_columns = random.randint(1, 2) * 5
        #key = (3, 1, 2, 5, 4) # Ordering of the columns for the key
        key = []
        for j in range(number_of_columns):
            key.append(j)
        random.shuffle(key)
        #print("key is " + str(key))
        result = "" # Store the result in this string
        plaintext = "" # Plaintext read from the input file

        file_input = open(input_file_name, "r")

        # Start our reading from a relatively random line from within the input file.
        random_line = random.randint(1, 45000)
    	#print("Reading from file at line " + str(random_line))
        for i in range(random_line):
            file_input.readline()
        # First, let's get a string of the specified length from our input file
        while (len(plaintext) != text_length):
            line = file_input.readline()
            for char in line:
                if char.isalpha(): # True if char is a letter (i.e. no special characters, no spaces, etc.)
                    plaintext += char.lower()
                    if (len(plaintext) == text_length):
                        break

        # Now let's encrypt result
        # First initialize our matrix columns by using a list
        columns = []
        for i in range(number_of_columns):
            columns.append('')
        # Then insert our plaintext into the columns
        for i in range(text_length):
            columns[i % number_of_columns] += plaintext[i]
        # Then rearrange the columns in the order specified by key
        columns_rearranged = []
        for c in key:
            columns_rearranged.append(columns[c - 1])
        # Then append characters to the result by going through our columns
        for i in range(int(text_length / number_of_columns)):
            for j in range(number_of_columns):
                result += columns_rearranged[j][i]


        # Write result to our output file
        file_output.write(result + " key: " + str(key) + ", reading from line " + str(random_line) + "\n")
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
