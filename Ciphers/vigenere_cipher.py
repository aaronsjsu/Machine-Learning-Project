"""
This file is used to implement a vigenere cipher. It works by reading input
from a specified txt file, filtering the characters to be lowercase letters
(discarding non-letter characters), and then encrypting the characters using
the vigenere cipher. See https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
for a brief description of the vigenere cipher. The result is then written to
a specified txt file.

__author__ = "Zizhen Huang and Aaron Smith"
__date__ = "11/4/2019"
"""


import random
import string
from multiprocessing import Process

def make_file(length):
	input_file_name = "brown_corpus.txt"
	output_file_name = "../Data/Vigenere Cipher/Random Key Random Length/text_length_" + str(length) + ".txt"
	vigenere_table_file = "vigenere_table.txt"
	text_length = length # Length of the character sequence to encrypt
	iters = 10000 # How many times to encrypt a string

	file_output = open(output_file_name, "w")

	for j in range(iters):
		key_length = random.randint(5, 25)
		# Generate random key of length 10
		key = "".join(random.choice(string.ascii_uppercase) for i in range(key_length))
		# Or use this default key
		#key = "VIGENERECIPHER" # Key length 10
		result = "" # Store the result in this string
		plaintext = "" # Plaintext read from the input file

		file_input = open(input_file_name, "r")

		# Read data from vigenere_table_file and place it in a 2d list.
		# This matrix represents all the possible caesar chiphers. The key
		# is then used to decide which shift to use to encrypt a character.
		with open(vigenere_table_file) as vigenere_file_data:
			vigenere_matrix = [line.split() for line in vigenere_file_data]

		# Start our reading from a relatively random line from within the input file.
		random_line = random.randint(1, 45000)
    	#print("Reading from file at line " + str(random_line))
		for i in range(random_line):
			file_input.readline()

		# Read plaintext line by line
		key_index = 0 # Represents current index/position in the key
		while (len(result) != text_length):
			line = file_input.readline()
			for char in line:
				if char.isalpha(): # True if char is a letter (i.e. no special characters, no spaces, etc.)
					key_index %= len(key) # Keep index in bounds of the length of the key
					row = ord(key[key_index]) - 65 # ord() function gets ascii value. row represents row in matrix
					col = (ord(char.lower()) - 97) # Get the column in our matrix
					result += vigenere_matrix[row][col].lower() # Get the encrypted character from the matrix
					key_index += 1 # Increment our index.
					if (len(result) == text_length):
						break

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
