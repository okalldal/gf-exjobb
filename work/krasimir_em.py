import numpy as np

#  occurrence_tuples : [([int],int)], init_probs : [double], convergence_threshold : double
def krasimir_em_algorithm(occurrence_tuples, init_probs, convergence_threshold):
    convergence_diff = convergence_threshold
    current_probs = init_probs
    while convergence_diff >= convergence_threshold:
        new_probs = np.zeros(current_probs.shape)
        for possibilities, count in occurrence_tuples:
            possibility_probabilities = current_probs[possibilities]
            total_probability = np.sum(possibility_probabilities)
            new_probs[possibilities] = possibility_probabilities*count/total_probability

