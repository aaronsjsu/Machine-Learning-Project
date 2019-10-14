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
output_file_name = "result.txt"
text_length = 1000 # Length of the character sequence to encrypt
key = random.randint(1, 25) # The amount to shift by
result = "" # Store the result in this string

file_input = open(input_file_name, "r")
file_output = open(output_file_name, "w")
# print("Shifting by " + str(key))


# Loop until the result string is the desired length
while len(result) != text_length:
    c = file_input.read(1).lower() # Reads 1 character at a time
    # c will already be lowercase
    ascii_code = ord(c) # Returns the ascii code of the character c
    # First eliminate spaces
    if (c == ' '):
        c = ''
    # Then eliminate non-letter characters
    elif (ascii_code < 97 or ascii_code > 122):
        c = ''
    # Else, shift the valid character by the amount in key
    else:
        c = ascii_code + key
        if (c > 122):
            c -= 26
        c = chr(c) # Convert ascii code back to character
    result += c # Add our character to our result


# Write result to our output file
file_output.write(result)

# Lastly, close our files
file_input.close()
file_output.close()
