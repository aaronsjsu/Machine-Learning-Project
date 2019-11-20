"""
Runs a random forest algorithm using our cipher data from ../../Data in order to classify
a ciphertext to belong to a particular cipher. Uses sklearn RandomForestClassifier.

__author__ = "Aaron Smith"
__date__ = "11/19/2019"
"""

from sklearn.ensemble import RandomForestClassifier

text_length = 1000 # How many characters in each ciphertext sample (options include 100, 200, 300, 500, 1000)
number_of_samples = 25000 # Total number of ciphertext samples to consider
number_of_data_points = 26 # Size of each vector representing each sample

file_names = [] # To keep track of all our data files
file_names.append("../../Data/Columnar Transposition Cipher/text_length_" + str(text_length) + ".txt")
file_names.append("../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt")
file_names.append("../../Data/Playfair Cipher/text_length_" + str(text_length) + ".txt")
file_names.append("../../Data/Hill Cipher/text_length_" + str(text_length) + ".txt")
file_names.append("../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt")


inputs = [] # To keep track of all our data file inputs
for file_name in file_names:
     inputs.append(open(file_name, "r"))

# Initialize our data sets
training_data = [[0 for i in range(number_of_data_points)] for j in range(number_of_samples)]
scoring_data = [[0 for i in range(number_of_data_points)] for j in range(number_of_samples)]

# First fill our training set. Each data file will get the same number of vectors in our data sets.
# For now, our two data sets will be filled using character counts.
samples_per_file = int(number_of_samples / len(inputs)) # How many samples to grab from each file
i = 0
for file_input in inputs:
    j = 0
    while (j != samples_per_file):
        line = file_input.readline()
        ciphertext = line[:text_length]
        for char in ciphertext:
            training_data[i][ord(char) - 97] += 1
        i += 1
        j += 1
i = 0
# Then fill our scoring set (using different data).
for file_input in inputs:
    j = 0
    while (j != samples_per_file):
        line = file_input.readline()
        ciphertext = line[:text_length]
        for char in ciphertext:
            scoring_data[i][ord(char) - 97] += 1
        i += 1
        j += 1

# Now fill our classifications list. This contains the corresponding classifications for our data vectors
# in our training and scoring sets. Each type of vector will get a different classifying value corresponding
# to it's cipher.
classifications = []
for j in range(len(inputs)):
    classifications += [j for i in range(samples_per_file)]

# Now build our k-nearest neighbor model, and test the accuracy of the scoring set.
model = RandomForestClassifier()
model.fit(training_data, classifications)
print(model.score(scoring_data, classifications))
