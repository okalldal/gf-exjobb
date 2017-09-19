import numpy as np
import scipy.stats
import itertools


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

