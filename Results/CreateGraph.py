"""
This file is used to create a bar graph using data obtained from various experimental results.
These results have been hard coded after running various programs in ../ML\ Experiments\.

__author__ = "Aaron Smith"
__date__ = "11/25/2019"
"""

import matplotlib.pyplot as plot

x_coordinates = [1, 2, 3, 4, 5]

#heights = [.835, .929, .935, .942, .945, .949]
#heights = [.923, .88, .829, .868]
#heights = [.815, .855, .876, .9, .935]
heights = [1, 1, 1, .903, .867]

# KNN = .835, Random Forest = .935, MLP = .945, SVM = .929, Adaboost = .942, VotingClassifier = .949
# Using bigram counts MLP=.927, both combined = .9432, using trigram counts mlp=.83, using all 3=.868

#labels = ["KNN", "SVM", "RF", "Adaboost", "MLP", "Voting"]
#labels = ["monogram", "bigram", "trigram", "all combined"]
#labels = ["100", "200", "300", "500", "1000"]
labels = ["columnar", "shift", "playfair", "hill", "vigenere"]

# plotting a bar chart
plot.bar(x_coordinates, heights, tick_label = labels,
        width = 0.8, color = ["blue"])

#plot.xlabel("Classifier")
#plot.xlabel("Statistic")
#plot.xlabel("Ciphertext Length")
plot.xlabel("Cipher vs Rest")

plot.ylabel("Accuracy")

#plot.title("Performance of Classifiers\n (text_length=1000, number_of_samples=25000)")
#plot.title("Ciphertext Statistic Performance using MLP\n (text_length=1000, number_of_samples=5000)")
#plot.title("Accuracy for each Ciphertext Length using RF\n (number_of_samples=25000)")
plot.title("Cipher vs Rest Accuracy using SVM\n (text_length=1000, number_of_samples=5000)")

plot.show()
