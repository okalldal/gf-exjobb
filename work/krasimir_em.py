import numpy as np

#  occurrence_tuples : [([int],int)], init_probs : np.[double], convergence_threshold : double
def krasimir_em_algorithm(occurrence_tuples, init_probs, convergence_threshold):
    convergence_diff = convergence_threshold
    current_probs = init_probs
    total_counts = sum([count for _, count in occurrence_tuples])
    while convergence_diff >= convergence_threshold:
        new_probs = np.zeros(current_probs.shape)
        for possibilities, count in occurrence_tuples:
            possibility_probabilities = current_probs[possibilities]  # numpy advanced indexing
            total_probability = np.sum(possibility_probabilities)
            new_probs[possibilities] = new_probs[possibilities] + possibility_probabilities*count/total_probability
        prob_quotients = new_probs / current_probs
        threshold_mask = prob_quotients > 1e-50*total_counts    # used for numpy advanced indexing to remove differences
                                                                # caused by numerical imprecision
        convergence_diff = np.sum(new_probs[threshold_mask]*np.log(prob_quotients[threshold_mask]))/total_counts
        current_probs = new_probs
    return current_probs/total_counts


if __name__ == '__main__':
    max_possibilities = 100
    max_simul_possibilities = 10
    max_count = 100
    unique_occurences = 10000
    convergence_threshold = 1e-10
    occurence_tuples = [([np.random.randint(max_possibilities)
                          for _ in range(np.random.randint(1,max_simul_possibilities))]
                         , np.random.randint(max_count))
                        for _ in range(unique_occurences)]
    init_probs = np.ones([max_possibilities])

    new_probs = krasimir_em_algorithm(occurence_tuples, init_probs,convergence_threshold)
    print(new_probs)
    print(sum(new_probs))