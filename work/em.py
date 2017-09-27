import numpy as np
from collections import defaultdict
import logging
def run(occurences, max_length=0):
    """ Run the EM algoritm
    
    The max_length arguments is the theoretical maximum length of the list 
    of possibilities. Its the length of all abstract functions in the unigram 
    model and length^2 for the bigram model. If max_length is set to zero, no
    smoothing is used.


    :param occurences: Counter
    :param int max_length: Used for smoothing. 
    :returns:
    """
    logging.info('Running to_ids')
    occurency_tuples, id2poss, poss2id = to_ids(occurences)
    logging.info('Total possibilities = {}.'.format(len(id2poss)))
    starting_probs = np.ones([len(id2poss)]) / 1e10
    logging.info('Running em_algorithm.')
    em_vals = em_algorithm(occurency_tuples,starting_probs, 1e-5)

    # add max_length to the counts to get laplace smoothing
    total_counts = max_length + np.sum(em_vals)
    
    probabilities = []
    for poss, count in zip(id2poss, np.nditer(em_vals, order='C')):
        probabilities.append((poss, count/total_counts))

    default_prob = 0 if max_length == 0 else 1/total_counts
    return defaultdict(lambda: default_prob, probabilities)


def to_ids(occurences):
    """ Converts the occurences to tuples with ids and counts

    the ids can later be transformed back into respective
    possibility using the conversion maps

    :param occurences:
    :return:
    """
    occurency_tuples = []
    possibility2id = dict()
    id2possibility = []
    current_id = 0
    for occurency, count in dict(occurences).items():
        possibility_ids = []
        for possibility in occurency:
            if possibility not in possibility2id.keys():
                possibility2id[possibility] = current_id
                id2possibility.append(possibility)
                possibility_ids.append(current_id)
                current_id = current_id + 1
            else:
                possibility_ids.append(possibility2id[possibility])
        if len(possibility_ids) > 0:
            occurency_tuples.append((possibility_ids, count))
    return occurency_tuples, id2possibility, possibility2id
    

def em_algorithm(occurrence_tuples, 
                 init_probs,
                 convergence_threshold=1e-5):
    """ The actual algorithm
    
    
    :param occurrence_tuples: has possibilities coded as IDs
    :type  occurrence_tuples: [([int],int)] 
    :param init_probs: np.[double]
    :param convergence_threshold: double
    :returns: np.[double]
    """
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
        threshold_mask = np.abs(prob_quotients) > 1e-50*total_counts    # used for numpy advanced indexing to remove differences
                                                                # caused by numerical imprecision
        convergence_diff = np.sum(new_probs[threshold_mask]*np.log(prob_quotients[threshold_mask]))/total_counts
        current_probs = new_probs
        #print(convergence_diff)
    return current_probs