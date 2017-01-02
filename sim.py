import pdb
import os
from collections import deque

def sim(pred, file='gcc_branch.out', **kwargs):
    trace = {}
    branches = []
    with open(file, 'r') as file_in:
        for line in file_in:
            register = line[2:8]
            result = int(line[9])
            trace.setdefault(register, []).append(result)
            branches.append([register, result])

    num_correct = pred(branches, l=kwargs['l'])
    total = sum(len(r) for r in trace.values())
    return (num_correct * 1.0/total)


class Counter:
    state = 2   # 1 and 2 predict do not take, 3 and 4 predict take
    def predict(self):
        if(self.state < 3):
            return -1
        if(self.state > 2):
            return 1

    def update(self, actual):
        if(actual == 1):
            self.state = self.state + 1
            if(self.state > 4):
                self.state = 4
        if(actual == -1):
            self.state = self.state - 1
            if(self.state < 1):
                self.state = 1
        return 


def saturating_counter(trace, l=1):

    c_list = {}
    num_correct = 0

    for br in trace:            # iterating through each branch
        if br[0] not in c_list:     # if no previous branch from this memory location 
            c_list[br[0]] = Counter()
        pr = c_list[br[0]].predict()
        actual_value = 1 if br[1] else -1
        c_list[br[0]].update(actual_value)
        if pr == actual_value:
            num_correct += 1
    return num_correct






# psuedocode: 
	# iterate over branches
		# look at memory address of new branch
		# compute prediction
		# check if correct
		# update weights
		# add new brancmicrophoneh result to FIFO of global_branch_history


# dictionary of perceptrons: map branch memory location to perceptron
# perceptrons: tuple consisting of a list with N weights and another list with the N historical outcomes


# class defines a single-layer perceptron for making a prediction about whether a given branch will be taken or not
#
# __init__
#   initializes the perceptron
#   @params
#       N: Length of branch history to be used for making prediction   
#   
# predict
#   makes a prediction as to whether the next branch will be taken or not
#   @params
#       global_branch_history: history of the past N branches
#   @returns
#       prediction: 1 if the branch is predicted to be taken and -1 if the branch is predicted to not be taken 
#       running_sum: raw output of the predictor
#
# update
#   @params
#       prediction: most recently calculated prediction
#       actual: used to determine if the prediction was correct
#       global_branch_history: history of the past N branches
#       running_sum: raw output of the predictor 
#
#

class Perceptron:
    weights = []
    N = 0
    bias = 0
    threshold = 0

    def __init__(self, N):
        self.N = N
        self.bias = 0
        self.threshold = 2 * N + 14                 # optimal threshold depends on history length
        self.weights = [0] * N      

    def predict(self, global_branch_history):
        running_sum = self.bias
        for i in range(0, self.N):                  # dot product of branch history with the weights
            running_sum += global_branch_history[i] * self.weights[i]
        prediction = -1 if running_sum < 0 else 1
        return (prediction, running_sum)

    def update(self, prediction, actual, global_branch_history, running_sum):
        if (prediction != actual) or (abs(running_sum) < self.threshold):   
            self.bias = self.bias + (1 * actual)
            for i in range(0, self.N):
                self.weights[i] = self.weights[i] + (actual * global_branch_history[i])

    def statistics(self):
        print "bias is: " + str(self.bias) + " weights are: " + str(self.weights)

# perceptron_pred
#   @params
#       trace: a list that contains pairs of branche memory locations and whether the branch was taken or not
#           ex: ['47aa6d', 1]
#       l: length of the branch history to use in making decisions
#   @returns
#       num_correct: the number of branches correctly predicted 
#

def perceptron_pred(trace, l=1):

    global_branch_history = deque([])
    global_branch_history.extend([0]*l)

    p_list = {}
    num_correct = 0

    for br in trace:            # iterating through each branch
        if br[0] not in p_list:     # if no previous branch from this memory location 
            p_list[br[0]] = Perceptron(l)
        results = p_list[br[0]].predict(global_branch_history)
        pr = results[0]
        running_sum = results [1]
        actual_value = 1 if br[1] else -1
        p_list[br[0]].update(pr, actual_value, global_branch_history, running_sum)
        global_branch_history.appendleft(actual_value)
        global_branch_history.pop()
        if pr == actual_value:
            num_correct += 1

    return num_correct



gcc = 'gcc_branch.out'
mcf = 'mcf_branch.out'
print "|Predictor|         |gcc accuracy|         |mcf accuracy|"

nn_gcc = sim(saturating_counter, file=gcc, l=16)
nn_mcf = sim(saturating_counter, file=mcf, l=16)
print "Saturating counter     %.5f             %.5f" % (nn_gcc, nn_mcf)


nn_gcc = sim(perceptron_pred, file=gcc, l=8)
nn_mcf = sim(perceptron_pred, file=mcf, l=8)
print "perceptron (depth 8)   %.5f             %.5f" % (nn_gcc, nn_mcf)

nn_gcc = sim(perceptron_pred, file=gcc, l=16)
nn_mcf = sim(perceptron_pred, file=mcf, l=16)
print "perceptron (depth 16)  %.5f             %.5f" % (nn_gcc, nn_mcf)

nn_gcc = sim(perceptron_pred, file=gcc, l=32)
nn_mcf = sim(perceptron_pred, file=mcf, l=32)
print "perceptron (depth 32)  %.5f             %.5f" % (nn_gcc, nn_mcf)


