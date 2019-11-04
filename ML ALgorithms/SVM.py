from sklearn import svm
import numpy as np

# Different elements to look at? Character counts?

text_length = 100
shift_cipher_file_name = "../Data/Shift Cipher/text_length_" + str(text_length) + ".txt"
columnar_transposition_cipher_file_name = "../Data/Columnar Transposition Cipher/Random Key Random Length/text_length_" + str(text_length) + ".txt"
number_of_samples = 1000 # i.e. number of vectors
number_of_data_points = 26 # i.e. height of vector

# Open our data files to be read from
shift_cipher_input = open(shift_cipher_file_name, "r")
columnar_transposition_cipher_input = open(columnar_transposition_cipher_file_name, "r")

# Initialize our data sets
training_set = [[0 for i in range(number_of_data_points)] for j in range(number_of_samples)]
scoring_set = [[0 for i in range(number_of_data_points)] for j in range(number_of_samples)]

# Now fill our data sets from our data files. Use character counts for data points in the vectors
# Fill first half of training set
i = 0
while (i != number_of_samples / 2):
    line = shift_cipher_input.readline()
    ciphertext = line[:text_length]
    for char in ciphertext:
        training_set[i][ord(char) - 97] += 1 # Training set will consist of letter frequency counts
    i += 1
# Fill second half of training set
while (i != number_of_samples):
    line = columnar_transposition_cipher_input.readline()
    ciphertext = line[:text_length]
    for char in ciphertext:
        training_set[i][ord(char) - 97] += 1 # Training set will consist of letter frequency counts
    i += 1
# Fill first half of scoring set
i = 0
while (i != number_of_samples / 2):
    line = shift_cipher_input.readline()
    ciphertext = line[:text_length]
    for char in ciphertext:
        scoring_set[i][ord(char) - 97] += 1 # Scoring set will consist of letter frequency counts
    i += 1
# Fill second half of scoring set
while (i != number_of_samples):
    line = columnar_transposition_cipher_input.readline()
    ciphertext = line[:text_length]
    for char in ciphertext:
        scoring_set[i][ord(char) - 97] += 1 # Scoring set will consist of letter frequency counts
    i += 1
# First half of our rows are a shift cipher. Classify as 1. Rest classify as -1.
classifications = [1 for i in range(int(number_of_samples / 2))] + [-1 for i in range(int(number_of_samples / 2))]


clf = svm.SVC(kernel='linear')
clf.fit(training_set, classifications)
print(clf)
print("Accuracy: " + str(clf.score(scoring_set, classifications)))
