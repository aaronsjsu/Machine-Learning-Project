"""
This file is used to implement the playfair cipher. It works by reading input from a
specified txt file at a random location, filtering the characters to be lowercase
letters (discarding non-letter characters), and then encrypting using a 5x5 matrix
as the key. The key is randomized. For details on how the playfair cipher works,
see https://en.wikipedia.org/wiki/Playfair_cipher.

The result is written to a txt file at the specified location. Uses multiprocessing
to run multiple instances of the cipher in parallel. That way large amounts of data
can be processed at a time, outputting to multiple files in order to get large
variations in the data.

__author__ = "Aaron Smith"
__date__ = "11/9/2019"
"""

import random
import string
from multiprocessing import Process
from collections import OrderedDict

def make_file(length):
    input_file_name = "brown_corpus.txt"
    output_file_name = "../Data/Playfair Cipher/text_length_" + str(length) + ".txt"
    text_length = length # Length of the character sequence to encrypt
    iters = 10000 # How many times to encrypt a string (different string each time)

    file_output = open(output_file_name, "w")

    for i in range(iters):
        # First, generate a random key phrase of random length.
        key_length = random.randint(7, 35)
        # This line builds the key phrase using random characters, making sure none are duplicated
        key_phrase = "".join(OrderedDict.fromkeys("".join(random.choice(string.ascii_lowercase) for i in range(key_length))))
        # Then add the rest of the alphabet to our key phrase
        rest_of_key = string.ascii_lowercase
        for char in key_phrase:
            rest_of_key = rest_of_key.replace(char, "")
        key_phrase = key_phrase + rest_of_key
        # Omit 'q' from key phrase
        key_phrase = key_phrase.replace("q", "")
        # Fill a 5x5 list with our key phrase
        key = []
        for j in range(5):
            key.append(list(key_phrase[(5 * j):(5 * (j + 1))]))

        result = "" # Store the result in this string
        file_input = open(input_file_name, "r")

        # Start our reading from a relatively random line from within the input file.
        random_line = random.randint(1, 45000)
        for j in range(random_line):
            file_input.readline()

        # Read plaintext line by line. Break once result string is desired length.
        while (len(result) != text_length):
            line = file_input.readline()
            # We want to read two characters at a time
            pair = ""
            for char in line:
                if char.isalpha(): # True if char is a letter (i.e. no special characters, no spaces, etc.)
                    pair += char.lower()
                    # If we have a pair, encrypt. Else, continue until we have two characters
                    if len(pair) == 2:
                        first_letter = pair[:1]
                        second_letter = pair[1]
                        # Split up pairs that have two of the same letter. Use 'x' as a spacer.
                        if first_letter == second_letter:
                            pair = second_letter
                            second_letter = "x"
                        else:
                            pair = ""
                        # Check for char 'q', which isn't in our key. Use 'x' as a placeholder
                        if first_letter == "q":
                            first_letter = "x"
                        elif second_letter == "q":
                            second_letter = "x"
                        # Find where the pairs of letters are in the key. Store these locations in these index lists.
                        index1 = []
                        index2 = []
                        for j in range(5):
                            row = key[j]
                            if first_letter in row:
                                index1.append(j)
                                index1.append(row.index(first_letter))
                            if second_letter in row:
                                index2.append(j)
                                index2.append(row.index(second_letter))
                        # Now encrypt
                        if index1[0] == index2[0]: # i.e. on the same row
                            result += key[index1[0]][(index1[1] + 1) % 5]
                            result += key[index1[0]][(index2[1] + 1) % 5]
                        elif index1[1] == index2[1]: # i.e. on the same column
                            result += key[(index1[0] + 1) % 5][index1[1]]
                            result += key[(index2[0] + 1) % 5][index1[1]]
                        else:  # i.e. letters don't lie on the same row or column
                            result += key[index1[0]][index2[1]]
                            result += key[index2[0]][index1[1]]
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
