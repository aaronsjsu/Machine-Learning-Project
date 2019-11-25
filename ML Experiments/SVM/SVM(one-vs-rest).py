
"""
Trains an SVM based on our cipher data from ../../Data using sklearn. Instead of using one SVM for
multi-class classification (as is done in ./SVM.py), this builds one svm for each class, each svm
is trained as one vs rest (e.g. shift cipher vs all the other ciphers). While the version shown
in ./SVM.py performs with similar accuracy (and is also constructed much easier), building multiple
SVM's this way can reveal which classes (ciphers) an SVM performs well on, and which one's it
doesn't. In order to build all these SVM's in a timely manner, the work is split between multiple
processes (and I admit, the code for this section looks a little ugly).

__author__ = "Aaron Smith"
__date__ = "11/24/2019"
"""

from sklearn import svm
from multiprocessing import Process, Manager
import numpy as np
import random

text_length = 1000
number_of_samples = 1000 # i.e. number of vectors (must be divisible by 1 + len(positive_cipher_file_names))
number_of_data_points = 26 # i.e. height of vector

print("Text length: " + str(text_length))
print("Number of samples: " + str(number_of_samples))

def get_data(text_length, number_of_samples, number_of_data_points, positive_cipher_file_names, negative_cipher_file_name):
    """
    Function to read data from some files and process it in order to train and score an SVM.
    In general, SVM generates a binary classifier. For our purposes, we want a multi-class
    classification. There are different ways to do this, in this file, we do it by generating
    a one-vs-all classification. This means that our positive data set will be obtained from
    multiple sources, while our negative set from one file. This can then be used to
    score a ciphertext, either as negative or positive. If it's positive, then more testing
    needs to be done to determine what category in the positive section it falls into.

    Args:
        text_length: The length of the ciphertext (options include 100, 200, 300, 500, 1000)
        number_of_samples: How many ciphertexts to use
        number_of_data_points: Should be 26, data just looks at letter frequency counts, thus 26 letters
        positive_cipher_file_names: Names of the files to be used for the positive classification
        negative_cipher_file_name: Name of the file to be used for the negative classification
    """
    # Open our data files to be read from
    positive_cipher_inputs = []
    for file_name in positive_cipher_file_names:
         positive_cipher_inputs.append(open(file_name, "r"))
    negative_cipher_input = open(negative_cipher_file_name, "r")

    # Initialize our data sets
    training_set = [[0 for i in range(number_of_data_points)] for j in range(number_of_samples)]
    scoring_set = [[0 for i in range(number_of_data_points)] for j in range(number_of_samples)]

    # Now fill our data sets from our data files. Use character counts for data points in the vectors.
    # Each file will contribute the same number of vectors in our data sets. (e.g., if there are 5 total files,
    # and number_of_samples = 1000, then each file will contribute 200 vectors, regardless if positive or negative).
    positive_ratio = len(positive_cipher_inputs) / (len(positive_cipher_inputs) + 1) # Percentage of our input files that are positive
    i = 0
    for file_input in positive_cipher_inputs:
        j = 0
        while (j != (number_of_samples * positive_ratio) / len(positive_cipher_inputs)):
            line = file_input.readline()
            ciphertext = line[:text_length]
            """ # For testing something else... instead of character counts, uses digraph counts
            prevChar = 0
            for char in ciphertext:
                if prevChar != 0:
                    if ord(char) - 97 == 0:
                        training_set[i][(ord(prevChar) - 97)] += 1
                    elif ord(prevChar) - 97 == 0:
                        training_set[i][(ord(char) - 97)] += 1
                    else:
                        training_set[i][(ord(char) - 97) * (ord(prevChar) - 97)] += 1
                prevChar = char
            """
            for char in ciphertext:
                training_set[i][ord(char) - 97] += 1
            i += 1
            j += 1
    # Fill last (negative) part of training set
    while (i != number_of_samples):
        line = negative_cipher_input.readline()
        ciphertext = line[:text_length]
        """
        prevChar = 0
        for char in ciphertext:
            if prevChar != 0:
                if ord(char) - 97 == 0:
                    training_set[i][(ord(prevChar) - 97)] += 1
                elif ord(prevChar) - 97 == 0:
                    training_set[i][(ord(char) - 97)] += 1
                else:
                    training_set[i][(ord(char) - 97) * (ord(prevChar) - 97)] += 1
            prevChar = char
        """
        for char in ciphertext:
            training_set[i][ord(char) - 97] += 1
        i += 1
    # Fill first (positive) part of scoring set
    i = 0
    for file_input in positive_cipher_inputs:
        j = 0
        while (j != (number_of_samples * positive_ratio) / len(positive_cipher_inputs)):
            line = file_input.readline()
            ciphertext = line[:text_length]
            """
            prevChar = 0
            for char in ciphertext:
                if prevChar != 0:
                    if ord(char) - 97 == 0:
                        scoring_set[i][(ord(prevChar) - 97)] += 1
                    elif ord(prevChar) - 97 == 0:
                        scoring_set[i][(ord(char) - 97)] += 1
                    else:
                        scoring_set[i][(ord(char) - 97) * (ord(prevChar) - 97)] += 1
                prevChar = char
            """
            for char in ciphertext:
                scoring_set[i][ord(char) - 97] += 1
            i += 1
            j += 1
    # Fill last (negative) part of scoring set
    while (i != number_of_samples):
        line = negative_cipher_input.readline()
        ciphertext = line[:text_length]
        """
        prevChar = 0
        for char in ciphertext:
            if prevChar != 0:
                if ord(char) - 97 == 0:
                    scoring_set[i][(ord(prevChar) - 97)] += 1
                elif ord(prevChar) - 97 == 0:
                    scoring_set[i][(ord(char) - 97)] += 1
                else:
                    scoring_set[i][(ord(char) - 97) * (ord(prevChar) - 97)] += 1
            prevChar = char
        """
        for char in ciphertext:
            scoring_set[i][ord(char) - 97] += 1
        i += 1
    # First half of our rows are classified as positive, i.e. 1. The rest is classified as -1.
    classifications = [1 for i in range(int(number_of_samples * positive_ratio))] + [-1 for i in range(number_of_samples - int(number_of_samples * positive_ratio))]
    return [training_set, scoring_set, classifications]


def generate_svm_model(positive_cipher_file_names, negative_cipher_file_name, svm_models, name):
    """
    Function to generate an SVM model using the get_data() function to determine what
    data to generate it with. Meant to be run by multiple processes.

    Args:
        positive_cipher_file_names: Names of the files to be used for the positive classification
        negative_cipher_file_name: Name of the file to be used for the negative classification
        svm_models: A dictionary that is used to pass data back to the parent process
        name: Name of the svm, used as a key into svm_models.
    """
    [training_set, scoring_set, classifications] = get_data(text_length, number_of_samples, number_of_data_points, positive_cipher_file_names, negative_cipher_file_name)
    svm_model = svm.SVC(kernel="poly", gamma="auto")
    svm_model.fit(training_set, classifications)
    #print(svm_model)
    print(name + " Accuracy: " + str(svm_model.score(scoring_set, classifications)))
    svm_models[name] = svm_model
    return svm_model


# Below here is a monstrosity that will generate various svm models in parallel using multiprocessing

processes = []
manager = Manager()
svm_models = manager.dict()


positive_cipher_file_names = []
positive_cipher_file_names.append("../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Columnar Transposition Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Playfair Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Hill Cipher/text_length_" + str(text_length) + ".txt")
negative_cipher_file_name = "../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt"
process = Process(target = generate_svm_model, args = (positive_cipher_file_names, negative_cipher_file_name, svm_models, "svm_model_vigenere_vs_rest"))
process.start()
processes.append(process)

positive_cipher_file_names = []
positive_cipher_file_names.append("../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Playfair Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Hill Cipher/text_length_" + str(text_length) + ".txt")
negative_cipher_file_name = "../../Data/Columnar Transposition Cipher/text_length_" + str(text_length) + ".txt"
process = Process(target = generate_svm_model, args = (positive_cipher_file_names, negative_cipher_file_name, svm_models, "svm_model_columnar_vs_rest"))
process.start()
processes.append(process)

positive_cipher_file_names = []
positive_cipher_file_names.append("../../Data/Columnar Transposition Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Playfair Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Hill Cipher/text_length_" + str(text_length) + ".txt")
negative_cipher_file_name = "../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt"
process = Process(target = generate_svm_model, args = (positive_cipher_file_names, negative_cipher_file_name, svm_models, "svm_model_shift_vs_rest"))
process.start()
processes.append(process)

"""
positive_cipher_file_names = []
positive_cipher_file_names = []
positive_cipher_file_names.append("../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt")
negative_cipher_file_name = "../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt"
process = Process(target = generate_svm_model, args = (positive_cipher_file_names, negative_cipher_file_name, svm_models, "svm_model_shift_vs_vigenere"))
process.start()
processes.append(process)
"""

positive_cipher_file_names = []
positive_cipher_file_names.append("../../Data/Columnar Transposition Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Playfair Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt")
negative_cipher_file_name =  "../../Data/Hill Cipher/text_length_" + str(text_length) + ".txt"
process = Process(target = generate_svm_model, args = (positive_cipher_file_names, negative_cipher_file_name, svm_models, "svm_model_hill_vs_rest"))
process.start()
processes.append(process)

positive_cipher_file_names = []
positive_cipher_file_names.append("../../Data/Columnar Transposition Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt")
positive_cipher_file_names.append("../../Data/Hill Cipher/text_length_" + str(text_length) + ".txt")
negative_cipher_file_name = "../../Data/Playfair Cipher/text_length_" + str(text_length) + ".txt"
process = Process(target = generate_svm_model, args = (positive_cipher_file_names, negative_cipher_file_name, svm_models, "svm_model_playfair_vs_rest"))
process.start()
processes.append(process)

# Wait for processes to finish
for process in processes:
    process.join()
svm_model_vigenere_vs_rest = svm_models["svm_model_vigenere_vs_rest"]
svm_model_columnar_vs_rest = svm_models["svm_model_columnar_vs_rest"]
svm_model_shift_vs_rest = svm_models["svm_model_shift_vs_rest"]
#svm_model_shift_vs_vigenere = svm_models["svm_model_shift_vs_vigenere"]
svm_model_hill_vs_rest = svm_models["svm_model_hill_vs_rest"]
svm_model_playfair_vs_rest = svm_models["svm_model_playfair_vs_rest"]



# Now that we have our SVM models, let's see if we can use them to correctly tell which cipher each ciphertext corresponds with.
class type: # Use this as an ENUM
    COLUMNAR = 0
    SHIFT = 1
    PLAYFAIR = 2
    HILL = 3
    VIGENERE = 4
    OTHER = 5

def determine_cipher(ciphertext):
    """
    Function that uses our trained SVM models to attempt to classify the ciphertext as
    belonging to a shift cipher (returns 2), vigenere cipher (returns 1), or a
    columnar transposition cipher (returns 0).

    Args:
        ciphertext: The ciphertext to analyze
    """
    # Put ciphertext into a list of character counts.
    test_matrix = [0 for i in range(number_of_data_points)]
    for char in ciphertext:
        test_matrix[ord(char) - 97] += 1
    # Now use predict() method using our trained SVM models.
    if (svm_model_columnar_vs_rest.predict([test_matrix]) == [-1]):
        return type.COLUMNAR
    elif (svm_model_shift_vs_rest.predict([test_matrix]) == [-1]):
        return type.SHIFT
    elif (svm_model_playfair_vs_rest.predict([test_matrix]) == [-1]):
        return type.PLAYFAIR
    elif (svm_model_hill_vs_rest.predict([test_matrix]) == [-1]):
        return type.HILL
    elif (svm_model_vigenere_vs_rest.predict([test_matrix]) == [-1]):
        return type.VIGENERE
    else:
        # If none of the svm's classify it as one of our ciphertexts, then it is most likely vigenere,
        # since vigenere cipher is the most common one to not be classified correctly.
        return type.VIGENERE


count = 100
accuracies = []

# Test columnar transposition cipher detection
file_input = open("../../Data/Columnar Transposition Cipher/text_length_" + str(text_length) + ".txt", "r")
for j in range(random.randint(number_of_samples, number_of_samples * 2)):
    file_input.readline()
file_input.readline()
count_correct = 0
for i in range(count):
    if (determine_cipher(file_input.readline()[:text_length]) == type.COLUMNAR):
        count_correct += 1
accuracies.append(count_correct / count)
print("Percentage correctly classified as columnar: " + str(count_correct / count))

# Test shift cipher detection
file_input = open("../../Data/Shift Cipher/text_length_" + str(text_length) + ".txt", "r")
for j in range(random.randint(number_of_samples, number_of_samples * 2)):
    file_input.readline()
file_input.readline()
count_correct = 0
for i in range(count):
    if (determine_cipher(file_input.readline()[:text_length]) == type.SHIFT):
        count_correct += 1
accuracies.append(count_correct / count)
print("Percentage correctly classified as shift: " + str(count_correct / count))

# Test playfair cipher detection
file_input = open("../../Data/Playfair Cipher/text_length_" + str(text_length) + ".txt", "r")
for j in range(random.randint(number_of_samples, number_of_samples * 2)):
    file_input.readline()
file_input.readline()
count_correct = 0
for i in range(count):
    if (determine_cipher(file_input.readline()[:text_length]) == type.PLAYFAIR):
        count_correct += 1
accuracies.append(count_correct / count)
print("Percentage correctly classified as playfair: " + str(count_correct / count))

# Test hill cipher detection
file_input = open("../../Data/Hill Cipher/text_length_" + str(text_length) + ".txt", "r")
for j in range(random.randint(number_of_samples, number_of_samples * 2)):
    file_input.readline()
file_input.readline()
count_correct = 0
for i in range(count):
    if (determine_cipher(file_input.readline()[:text_length]) == type.HILL):
        count_correct += 1
accuracies.append(count_correct / count)
print("Percentage correctly classified as hill: " + str(count_correct / count))

# Test vigenere cipher detection
file_input = open("../../Data/Vigenere Cipher/text_length_" + str(text_length) + ".txt", "r")
for j in range(random.randint(number_of_samples, number_of_samples * 2)):
    file_input.readline()
file_input.readline()
count_correct = 0
for i in range(count):
    if (determine_cipher(file_input.readline()[:text_length]) == type.VIGENERE):
        count_correct += 1
accuracies.append(count_correct / count)
print("Percentage correctly classified as vigenere: " + str(count_correct / count))

print("average: " + str(sum(accuracies) / 5))


# This is testing for something else
"""
file_input = open("../ciphers_to_test.txt", "r")
for file in file_input:
    print(determine_cipher(file[5:105].rstrip()))
"""
