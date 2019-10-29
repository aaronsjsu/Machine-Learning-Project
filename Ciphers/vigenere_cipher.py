"""
This file is used to implement a vigenere cipher. It works by
reading input from a specified txt file, filtering the characters to be
lowercase letters (discarding non-letter characters), and then encrypting
the characters using the vigenere cipher. See
https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
for a brief description. The result is then written to a specified txt file.
__author__ = "Zizhen Huang"
__date__ = "10/28/2019"
"""


input_file_name = "brown_corpus.txt"
output_file_name = "result.txt"
key = "VIGENERECIPHER" # length 10 and serves as row in the table
result = "" # Store the result in this string
plaintext = "" # Plaintext read from the input file

file_input = open(input_file_name, "r")
file_output = open(output_file_name, "w")

# remember we just wnat to lower case and letters
# create a The Vigenère square or Vigenère table,
# by reading the data from vigenere_table.txt 
with open("vigenere_table.txt") as vigenere_table_data:
	Vigenère_square = [line.split() for line in vigenere_table_data]

# another way here is to read the whole file into plaintext and traverse
# here we just read line by line and that is why we make index_for_key global
index_for_key = 0
for plaintext in file_input:
	for char in plaintext:
		if char.isalpha():
			index_for_key %= len(key) # rotate the key w.r.t index_for_key
			row = ord(key[index_for_key]) - 65 # get the row 
			index_for_key += 1
			if char.islower():				
				col = (ord(char) - 97) # get the column
				result += Vigenère_square[row][col] # get the encryption char from the table
			elif char.isupper():				
				col = (ord(char) - 65)
				result += Vigenère_square[row][col]

# Write result to our output file
file_output.write(result)

# Lastly, close our files
file_input.close()
file_output.close()






