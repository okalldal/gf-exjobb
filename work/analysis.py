import numpy as np
import scipy.stats
import itertools
from collections import defaultdict


def run_analysis(language_distributions, combined_distribution):
    print("Calculating statistics for: {}".format(list(language_distributions.keys())))
    print("\tEntropies and KL-divergencies from combined distribution:")

    all_keys = list(combined_distribution.keys())
    dist_arrays = dict()
    combined_dist_array = np.array([combined_distribution[key] for key in all_keys])
    for name, dist in language_distributions.items():
        dist_array = np.array([dist[key] for key in all_keys])
        dist_arrays[name] = dist_array
        entropy = scipy.stats.entropy(dist_array)
        kl_dist = scipy.stats.entropy(dist_array, combined_dist_array)
        print("\t\t{}: {}, {}".format(name, entropy, kl_dist))
    #print("\tKL-divergencies:")



def bigram_marginal_distributions(bigram_probability_dictionary):
    '''
    Doesn't handle smoothed distributions if given with defaultdict.
    :param bigram_probability_dictionary:
    :return:
    '''
    headword_probabilities = defaultdict(lambda: 0)
    dependent_word_probabilities = defaultdict(lambda: 0)
    for key, probability in bigram_probability_dictionary:
        head = key[0]
        dependent = key[1]
        headword_probabilities[head] = headword_probabilities[head] + probability
        dependent_word_probabilities[dependent] = dependent_word_probabilities[dependent] + probability
    return dependent_word_probabilities, headword_probabilities


def bigram_conditional_probabilities(bigram_probability_dictionary, marginal_probability_dictionary):
    conditional_probabilities = dict()
    for key, probability in bigram_probability_dictionary:
        head = key[0]
        conditional_probabilities[key] = probability / marginal_probability_dictionary[head]


def calculate_tree_probability(tree_tuple_list, bigram_probabilities, unigram_probabilities, interpolation_constant = 0.5):
    probability = 1
    for node, head in tree_tuple_list:
        c = interpolation_constant
        node_cond_prob = c*bigram_probabilities[(node, head)]+(1-c)*unigram_probabilities(node)
        probability = probability * node_cond_prob
    return probability
