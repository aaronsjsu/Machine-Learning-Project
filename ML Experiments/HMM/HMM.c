#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

/**
 * Hidden Markov Model program for analyzing English text. Reads in text from a specified file (in this
 * case, BrownCorpus.txt). This file can be found at http://www.sls.hawaii.edu/bley-vroman/brown.txt.
 * It's based off the Brown Corpus (a general text collection). The file takes some number of characters
 * from that text and uses it for our data sample. The characters are filtered out in such a way that only
 * lowercase letters and spaces are considered (uppercase letters are converted to lowercase). Thus, our
 * alphabet consists of 27 characters. The program then trains a model (lambda = (A, B, Pi)) using our
 * data. We initialize the matrices in our model to be approximately uniform (but not exactly uniform).
 * It then attempts to find the optimal model using the Baum-Welch algorithm. The program can also run
 * random restarts to better optimize the model (after all, HMM's can be seen as a discrete hill climb).
 * This program was used to satisfy hw assignments in a machine learning class using the textbook
 * "Introduction to Machine Learning with Applications in Information Security". Various problems
 * were analyzed, including trying to find the key for the zodiac 408 cipher. To compile, use
 * "gcc -o HMM HMM.c -lm", then run it with ./HMM.
 *
 * Author: Aaron Smith
 * Last Edited: 9/17/2019
 */


// Initial/Given data
#define T 1000 // Length of observation sequence
#define N 5 // Number of states in the model
#define M 26 // Number of observation symbols. Zodiac cipher had 53
int O[T]; // Observation sequence (with char's converted to int's)

// Variables for our model. Initialized in initModel.
double A[N][N] = {0}; // State transition probabilities
double B[N][M] = {0}; // Observation probability matrix
double Pi[N] = {0}; // Initial state distribution

// Used to keep track of the optimum model while running random restarts
double optimumA[N][N] = {0};
double optimumB[N][M] = {0};
double optimumPi[N] = {0};
double optimumLogProb = -INFINITY;
// Other Variables
double c[T];
double alphas[T][N];
double betas[T][N];
double gammas[T][N];
double digammas[T][N][N];
double epsilon = .0000001;
double delta = 0;
double logProb = 0;
double oldLogProb = -INFINITY;
int iters = 0; // Keeps track of the current iteration
int minIters = 100; // Specifies the minimum number of iterations to perform
int readSize = 100; // How many characters to read at a time from our txt file
int printOn = 0; // If printOn set to 1, the model is printed each round
int randomRestarts = 100; // Number of random restarts to perform to try to get a better result.
char fileName[] = "test2.txt"; // Input text. key: BHZFFX, reading from line 6860


// Function to print our model and relevant data in a readable format.
void printModel() {
    double sum[N] = {0};

    printf("Iteration: %d\n", iters);
    printf("logProb: %f\n",logProb);

    // Print A
    printf("A:\n");
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            printf(" %f ", A[i][j]);
            sum[0] += A[i][j];
        }
        printf(", sum = %f\n", sum[0]);
        sum[0] = 0;
    }
    // Print B
    int accuracy = 0;
    printf("B^T:\n");
    for (int i = 0; i < M; i++) {
        if (i == 26) {
            printf("' ' | ");
        } else {
            printf(" %c | ", i + 'a');
        }
        double Max = 0;
        int maxIn = 0;
       
        for (int j = 0; j < N; j++) {
            printf("%f ", B[j][i]);
            if(Max < B[j][i]){
                maxIn = j;              
                Max = B[j][i];
            }
            sum[j] += B[j][i];
        }
        printf("Max = %f, letter = %c\n", Max, 'a'+maxIn);
        // check the key
        int key = 11;
        if((maxIn + key) % 26 == i){
                accuracy++;
        }

    }

    // determine the final accuracy by verifying the matching letters
    printf("\n\naccuracy: %d\n\n", accuracy);
    printf("sum[0] = %f", sum[0]);
    for (int i = 1; i < N; i++) {
        printf(", sum[%d] = %f", i, sum[i]);
    }

    // Print Pi
    printf("\nPi:\n");
    sum[0] = 0;
    for (int i = 0; i < N; i++) {
        printf(" %f ", Pi[i]);
        sum[0] += Pi[i];
    }
    printf(", sum = %f\n\n", sum[0]);
}


// Function to initialize our model. Each of the matrices in our model have to be row
// stochastic and roughly uniform (though not uniform). Below is a basic method to
// initialize our model to contain somewhat random values. 
int initModel() {


    double sumPi = 0;
    for (int i = 0; i < N - 1; i++) {
        // First, get a small random value.
        double randomVal = (double)((rand() % 9) + 1) * .00351;
        // Now add or subtract that to our uniform value.
        if (rand() % 2 == 0) {
            Pi[i] = (1.0 / N) + randomVal;
        } else {
            Pi[i] = (1.0 / N) - randomVal;
        }
        sumPi += Pi[i]; // Keep track of a sum of all our row's values
    }
    // Make the last element in the row such that the row adds to 1 (i.e. is row stochastic).
    Pi[N - 1] = 1 - sumPi;

    double sumA[N] = {0};
    for (int i = 0; i < N; i++) {
        sumA[i] = 0;
        for (int j = 0; j < N - 1; j++) {
            // First, get a small random value.
            double randomVal = (double)((rand() % 9) + 1) * .00238;
            // Now add or subtract that to our uniform value.
            if (rand() % 2 == 0) {
                A[i][j] = (1.0 / N) + randomVal;
            } else {
                A[i][j] = (1.0 / N) - randomVal;
            }
            sumA[i] += A[i][j]; // Keep track of a sum of all our row's values
        }
        // Make the last element in each row such that the row adds to 1 (i.e. is row stochastic).
        A[i][N - 1] = 1 - sumA[i];
    }

    double sumB[N] = {0};
    for (int i = 0; i < N; i++) {
        sumB[i] = 0;
        for (int j = 0; j < M - 1; j++) {
            // First, get a small random value.
            double randomVal = (double)((rand() % 9) + 1) * .000426;
            // Now add or subtract that to our uniform value.
            if (rand() % 2 == 0) {
                B[i][j] = (1.0 / M) + randomVal;
            } else {
                B[i][j] = (1.0 / M) - randomVal;
            }
            sumB[i] += B[i][j]; // Keep track of a sum of all our row's values
        }
        // Make the last element in each row such that the row adds to 1 (i.e. is row stochastic).
        B[i][M - 1] = 1 - sumB[i];
    }
    return 0;
}


// Function that implements the forward algorithm. 
int alphaPass() {
    // First compute all our alphas[0][i]
    c[0] = 0;
    for (int i = 0; i < N; i++) {
        alphas[0][i] = Pi[i] * B[i][O[0]];
        c[0] += alphas[0][i];
    }

    // Then we'll scale the alphas[0][i]
    c[0] = 1 / c[0];
    for (int i = 0; i < N; i++) {
        alphas[0][i] *= c[0];
    }
    // Then compute all the alphas[t][i]
    for (int t = 1; t < T; t++) {
        c[t] = 0;
        for (int i = 0; i < N; i++) {
            alphas[t][i] = 0;
            for (int j = 0; j < N; j++) {
                alphas[t][i] += (alphas[t - 1][j] * A[j][i]);
            }
            alphas[t][i] *= B[i][O[t]];
            c[t] += alphas[t][i];
        }
        // And we'll scale our alphas[t][i]
        c[t] = 1 / c[t];
        for (int i = 0; i < N; i++) {
            alphas[t][i] *= c[t];
        }
    }
    return 0;
}


// Function that implements the backwards algorithm. 
int betaPass() {
    // First, let betas[T-1][i] = 1 scaled by c[t-1].
    for (int i = 0; i < N; i++) {
        betas[T - 1][i] = c[T - 1];
    }

    // Now calculate betas.
    for (int t = T - 2; t >= 0; t--) {
        for (int i = 0; i < N; i++) {
            betas[t][i] = 0;
            for (int j = 0; j < N; j++) {
                betas[t][i] += A[i][j] * B[j][O[t + 1]] * betas[t + 1][j];
            }
            // Then scale our betas[t][i] by same scale factor used on alphas[t][i]
            betas[t][i] *= c[t];
        }
    }
    return 0;
}


// Function to compute gammas and di-gammas.
int computeGammas() {
    for (int t = 0; t < T - 1; t++) {
        double denom = 0;
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                denom += alphas[t][i] * A[i][j] * B[j][O[t + 1]] * betas[t + 1][j];
            }
        }
        for (int i = 0; i < N; i++) {
            gammas[t][i] = 0;
            for (int j = 0; j < N; j++) {
                digammas[t][i][j] = (alphas[t][i] * A[i][j] * B[j][O[t + 1]] * betas[t + 1][j]) / denom;
                gammas[t][i] += digammas[t][i][j];
            }
        }
    }
    double denom = 0;
    for (int i = 0; i < N; i++) {
        denom += alphas[T - 1][i];
    }
    for (int i = 0; i < N; i++) {
        gammas[T - 1][i] = alphas[T - 1][i] / denom;
    }
    return 0;
}


// Re-estimate our model (A, B Pi) given our gammas and di-gammas. 
int reEstimateModel() {
    // Re-estimate Pi
    for (int i = 0; i < N; i++) {
        Pi[i] = gammas[0][i];
    }

    // Re-estimate A
    // for (int i = 0; i < N; i++) {
    //     for (int j = 0; j < N; j++) {
    //         double numer = 0;
    //         double denom = 0;
    //         for (int t = 0; t < T - 1; t++) {
    //             numer += digammas[t][i][j];
    //             denom += gammas[t][i];
    //         }
    //         A[i][j] = numer / denom;
    //     }
    // }

    // Re-estimate B
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            double numer = 0;
            double denom = 0;
            for (int t = 0; t < T; t++) {
                if (O[t] == j) {
                    numer += gammas[t][i];
                }
                denom += gammas[t][i];
            }
            B[i][j] = numer / denom;
        }
    }

    return 0;
}


// Compute the log of the score
int logP(){
    logProb = 0;
    for (int i = 0; i < T; i++) {
        logProb += log(c[i]);
    }
    logProb = -logProb;
    return 0;
}


// Given the plaintext O[], encrypt it by shifting a random amount. Return the shift amount (number between 1 and 25).
int encryptPlainText() {
    int shift = (rand() % M - 2) + 1;
    printf("Encryption shift: %d\n", shift);
    for (int i = 0; i < T - 1; i++) {
        O[i] += shift;
        if (O[i] >= M) {
            O[i] -= M;
        }
        if (O[i] < 0 || O[i] > M - 1) { // Error check
            return -1;
        }
    }
    return shift;
}

// Used to create a digraph frequency matrix (i.e. a matrix counting the frequency that one letter
// goes to another, thus a 26x26 matrix). The result of running this on a million characters is
// in digraphFrequencyMatrix[] above.
int createDigraphFrequencyMatrix() {
    // Add 5 to each entry so that we get no zero entries (which would give us bad data
    // if we initialize our A matrix with zero entries
    for (int i = 0; i < 26; i++) {
        for (int j = 0; j < 26; j++) {
            A[i][j] = 5;
        }
    }
    // Then tally up all the occurrences
    for (int i = 0; i < T - 1; i++) {
        A[O[i]][O[i + 1]]++;
    }
    // Then normalize so that rows are row stochastic (add up to 1).
    int rowSum = 0;
    for (int i = 0; i < 26; i++) {
        rowSum = 0;
        for (int j = 0; j < 26; j++) {
            rowSum += A[i][j];
        }
        for (int j = 0; j < 26; j++) {
            A[i][j] /= rowSum; // Divide by rowSum to normalize
        }
    }
    // Then print our results
    for (int i = 0; i < 26; i++) {
        printf("%c   ", i + 'a');
        for (int j = 0; j < 26; j++) {
            printf("%c-%f ", j + 'a', A[i][j]);
        }
        printf("\n");
    }

    return 0;
}


// Initialize our A matrix to be equal to a digraph frequency matrix.
// A needs to be 26x26.
int initAToDigraphFrequencyMatrix() {
    for (int i = 0; i < 26; i++) {
        for (int j = 0; j < 26; j++) {
            A[i][j] = digraphFrequencyMatrix[i][j];
        }
    }
    return 0;
}

// Copies the current model into our optimum model variables for safekeeping.
int saveOptimumModel() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            optimumA[i][j] = A[i][j];
        }
    }
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            optimumB[i][j] = B[i][j];
        }
    }
    for (int i = 0; i < N; i++) {
        optimumPi[i] = Pi[i];
    }
    optimumLogProb = logProb;
    return 0;
}
// Copies the optimum model found back into our model variables. Useful
// for printing the model since my printModel() function is hard coded
// to print the model using the default variables.
int restoreOptimumModel() {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i][j] = optimumA[i][j];
        }
    }
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            B[i][j] = optimumB[i][j];
        }
    }
    for (int i = 0; i < N; i++) {
        Pi[i] = optimumPi[i];
    }
    logProb = optimumLogProb;
    return 0;
}

int main(int argc, char **argv) {
    srand(time(NULL)); // A seed in order to use rand()

    printf("Starting\n");

    // Now we'll open the file to get the text
    printf("opening %s\n\n", fileName);
    FILE *fptr;
    fptr = fopen(fileName, "r");
    if (!fptr) { printf("Error opening file\n"); }

    // Now we'll read from the text, readSize characters at a time, until we get T characters total.
    // We'll filter the text as we go to only get lowercase letters (and possibly spaces).
    char line[readSize];
    int i = 0; // i is index into O[]
    int currentIteration = 0; // Keep track of how many fread() calls.
    while (i < T) { // Read until we get T valid characters
        if (fread(line, sizeof(char), readSize, fptr) < readSize) { printf("Error reading file\n"); }
        // Then transfer text to our observation sequence matrix (converting char's to int's)
        for (int j = 0; j < readSize; j++) { // j is index into line[]
            // First deal with spaces.
            if (line[j] == ' ' && M == 27) { // If M == 27 then spaces count too
                O[i] = 26;
            } else if (line[j] >= 'A' && line[j] <= 'Z') { // Deal with uppercase letters
                O[i] = line[j] - 'A';
            } else if (line[j] >= 'a' && line[j] <= 'z') { // lowercase
                O[i] = line[j] - 'a';
            } else {
                continue;
            }
            //printf(" %c ", O[i] + 'a');
            i++; // Increment our index
            if (O[i] < 0 || O[i] > M - 1) { // Error check
                return -1;
            }
        }
    }
    fclose(fptr);


    /*
    // Copy zodiac 408 into O[]
    for (int i = 0; i < T; i++) {
        O[i] = zodiac408[i];
    }
     */
    //createDigraphFrequencyMatrix();
    //int shift = encryptPlainText();

    // Initialize our model
    initModel(); // Normal initialization
    //initAToDigraphFrequencyMatrix();// Sometimes we want to initialize A based on our digraph frequency matrix.
    printf("Initial model:\n");
    printModel();

    printf("Running with %d random restarts\n", randomRestarts);
    printf("N: %d; M: %d", N, M);
    // Run the entire process randomRestarts amount of times
    i = 0;
    int s = 0;
    while (i < randomRestarts) {
        // Re-estimate model at least minIters times and stop when the change in the estimation
        // is statistically insignificant (i.e. delta < epsilon).
        iters = 0;
        while (iters < minIters || delta > epsilon) {
            alphaPass();
            betaPass();
            computeGammas();
            reEstimateModel();
            logP();
            delta = fabs(logProb - oldLogProb);
            oldLogProb = logProb;
            iters++;
            if (printOn) { printModel(); }
        }
        //if(s == 20){
          printf("Iter %d. comparing %f to optimum %f \n", i, logProb, optimumLogProb);
          s = 0; 
        //}
        if (logProb > optimumLogProb) {
                // If this model is better than our optimum model, set our optimum model to it
                saveOptimumModel();
                
        }
        
        
        i++;
        s++;
        initModel(); // Re-initialize our model (i.e. random restart), try again to see if we get better results
        //initAToDigraphFrequencyMatrix(); // make A the same as the original
    }

    restoreOptimumModel();
    printf("Best model found: \n");
    printModel();

    printf("done\n");
    return 0;
}
