import numpy as np
from scipy.misc import comb

# Simple coin toss EM example
# http://ai.stanford.edu/~chuongdo/papers/em_tutorial.pdf
# Generate hidden parameters

coin_biases = np.array([0.3, 0.7])

number_of_sets = 5
set_size = 10

coin_choices = [1, 0, 0, 1, 0] #np.random.randint(2, size=number_of_sets)
data_set = [5, 9, 8, 4, 7] #np.zeros([number_of_sets])

#for i in range(number_of_sets):
#    coin_choice = coin_choices[i]
#    data_set[i] = np.random.binomial(set_size, coin_biases[coin_choice])

print(data_set)
print(coin_choices)

bias_estimate = np.array([0.6, 0.5])

iterations = 10
for i in range(iterations):
    coin_likelihoods = np.zeros([number_of_sets, 2])
    coin_prob = np.zeros([number_of_sets, 2])
    for i in range(number_of_sets):
        k = data_set[i]
        n = set_size
        coin_likelihoods[i, 0] = comb(n, k)\
                                 * np.power(bias_estimate[0], k)\
                                 * np.power(1-bias_estimate[0], n-k)
        coin_likelihoods[i, 1] = comb(n, k) \
                                 * np.power(bias_estimate[1], k) \
                                 * np.power(1 - bias_estimate[1], n - k)
        coin_prob[i, :] = coin_likelihoods[i, :]\
                          / (coin_likelihoods[i, 0]+coin_likelihoods[i, 1])
    tot_A = np.sum(coin_prob[:, 0])*10
    tot_B = np.sum(coin_prob[:, 1])*10
    head_A = np.sum(coin_prob[:, 0]*data_set)
    head_B = np.sum(coin_prob[:, 1]*data_set)

    bias_estimate[0] = head_A/tot_A
    bias_estimate[1] = head_B/tot_B

    print(coin_prob)
    print(bias_estimate)




print("Finished.")