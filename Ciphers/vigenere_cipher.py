"""
This file is used to implement a vigenere cipher. It works by reading input
from a specified txt file, filtering the characters to be lowercase letters
(discarding non-letter characters), and then encrypting the characters using
the vigenere cipher. See https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
for a brief description of the vigenere cipher. The result is then written to
a specified txt file.

__author__ = "Zizhen Huang and Aaron Smith"
__date__ = "11/3/2019"
"""


input_file_name = "brown_corpus.txt"
output_file_name = "result.txt"
vigenere_table_file = "vigenere_table.txt"
text_length = 1000 # Length of the character sequence to encrypt
key = "VIGENERECIPHER" # Key length 10
result = "" # Store the result in this string
plaintext = "" # Plaintext read from the input file

file_input = open(input_file_name, "r")
file_output = open(output_file_name, "w")

# Read data from vigenere_table_file and place it in a 2d list.
# This matrix represents all the possible caesar chiphers. The key
# is then used to decide which shift to use to encrypt a character.
with open(vigenere_table_file) as vigenere_file_data:
	vigenere_matrix = [line.split() for line in vigenere_file_data]

# Read plaintext line by line
key_index = 0 # Represents current index/position in the key
for line in file_input:
	for char in line:
		if char.isalpha(): # True if char is a letter (i.e. no special characters, no spaces, etc.)
			key_index %= len(key) # Keep index in bounds of the length of the key
			row = ord(key[key_index]) - 65 # ord() function gets ascii value. row represents row in matrix
			col = (ord(char.lower()) - 97) # Get the column in our matrix
			result += vigenere_matrix[row][col].lower() # Get the encrypted character from the matrix
			key_index += 1 # Increment our index.

# Write result to our output file
file_output.write(result)

# Lastly, close our files
file_input.close()
file_output.close()
