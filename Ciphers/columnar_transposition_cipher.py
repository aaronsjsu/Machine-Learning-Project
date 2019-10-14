"""
This file is used to implement a columnar transposition cipher. It works by
reading input from a specified txt file, filtering the characters to be
lowercase letters (discarding non-letter characters), and then encrypting
the characters using the columnar transposition cipher. See
http://practicalcryptography.com/ciphers/columnar-transposition-cipher/
for a brief description. The result is then written to a specified txt file.

__author__ = "Aaron Smith"
__date__ = "10/13/2019"
"""


input_file_name = "brown_corpus.txt"
output_file_name = "result.txt"
text_length = 1000 # Length of the character sequence to encrypt
number_of_columns = 5 # Number of columns for our columnar transposition
key = (3, 1, 2, 5, 4) # Ordering of the columns for the key
result = "" # Store the result in this string
plaintext = "" # Plaintext read from the input file

file_input = open(input_file_name, "r")
file_output = open(output_file_name, "w")


# First, let's get a string of the specified length from our input file
while len(plaintext) != text_length:
    c = file_input.read(1).lower() # Reads 1 character at a time
    # c will already be lowercase
    ascii_code = ord(c) # Returns the ascii code of the character c
    # First eliminate spaces
    if (c == ' '):
        c = ''
    # Then eliminate non-letter characters
    elif (ascii_code < 97 or ascii_code > 122):
        c = ''
    plaintext += c # Add our character to our result

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
for i in range(text_length / number_of_columns):
    for j in range(number_of_columns):
        result += columns_rearranged[j][i]


# Write result to our output file
file_output.write(result)

# Lastly, close our files
file_input.close()
file_output.close()
