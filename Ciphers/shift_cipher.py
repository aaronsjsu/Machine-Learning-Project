"""
This file is used to implement a shift cipher. It works by reading input
from a specified txt file, filtering the characters to be lowercase letters
(discarding non-letter characters), and then shifting the characters by a
random amount in the range of 1-25. It writes the result to a specified txt file.

__author__ = "Aaron Smith"
__date__ = "10/13/2019"
"""

import random

input_file_name = "brown_corpus.txt"
output_file_name = "../Data/Shift Cipher/text_length_100.txt"
text_length = 100 # Length of the character sequence to encrypt
iters = 10000 # How many times to encrypt a string

file_output = open(output_file_name, "w")
for i in range(iters):
	key = random.randint(1, 25) # The amount to shift by
	result = "" # Store the result in this string

	file_input = open(input_file_name, "r")

	#print("Shifting by " + str(key))

	# Start our reading from a relatively random line from within the input file.
	random_line = random.randint(1, 45000)
	#print("Reading from file at line " + str(random_line))
	for j in range(random_line):
		file_input.readline()
	# Read plaintext line by line. Break once result string is desired length.
	while (len(result) != text_length):
		line = file_input.readline()
		for char in line:
			if char.isalpha(): # True if char is a letter (i.e. no special characters, no spaces, etc.)
				char = ord(char.lower()) + key # Convert character to ascii code. Shift by key amount.
				if (char > 122):
					char -= 26
				result += chr(char) # Convert ascii code back to character. Add to result.
				if (len(result) == text_length):
					break

	# Write result to our output file
	file_output.write(result + "\n")
	file_input.close()

file_output.close()
