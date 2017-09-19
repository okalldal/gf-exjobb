import numpy as np
import scipy
import itertools


def run_analysis(**distributions):
    print("Calculating statistics for: {}".format(list(distributions.keys())))
    print("\tEntropies:")

    all_keys = list(set(itertools.chain(*distributions.values())))
    dist_arrays = dict()
    for name, dist in distributions:
        dist_array = np.array([dist[key] for key in all_keys])
        dist_arrays[name] = dist_array
        print("\t\t{}: {}".format(name, scipy.stats.entropy(dist_array)))
    print("\tKL-divergencies:")
    for distribution_names, distributions in itertools.permutations(dist_arrays.items()):
        print("\t\t{}: {}".format(distribution_names, scipy.stats.entropy(*distributions)))

