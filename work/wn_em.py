import numpy as np
import logging

#wc lang -> lemma -> count, funs [synsets], pd lang -> lemma -> [synsets]
def run(word_counts, funs, possibility_dicts):
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
    wc_by_id, pd_by_id, id2word, word2id, id2fun, fun2id = to_ids(word_counts, possibility_dicts, funs)
    logging.info('Total functions = {}.'.format(len(id2fun)))
    starting_probs = np.ones([len(id2fun)]) / 1e10
    starting_word_probs = dict()
    for lang in word_counts.keys():
        logging.info('Total words in {} = {}.'.format(lang, len(id2word[lang])))
        starting_word_probs[lang] = [np.ones([len(poss)])/len(poss) for poss in pd_by_id[lang]]
    logging.info('Running em_algorithm.')
    probs, word_probs = em_algorithm(wc_by_id, starting_probs, starting_word_probs, pd_by_id, 1e-5)

    # add max_length to the counts to get laplace smoothing
    #total_counts = max_length + np.sum(probs)
    
    probabilities = dict()
    for fun, prob in zip(id2fun, np.nditer(probs, order='C')):
        probabilities[fun]=prob
    return probabilities


def to_ids(word_counts, possibility_dicts, funs):
    """ Converts the occurences to tuples with ids and counts

    the ids can later be transformed back into respective
    possibility using the conversion maps

    :param occurences:
    :return:
    """
    fun2id = dict()
    id2fun = []
    current_id = 0
    for fun in funs:
        fun2id[fun] = current_id
        id2fun.append(fun)
        current_id = current_id+1

    word2id = dict()
    id2word=dict()
    wc_by_id = dict()
    pd_by_id = dict()
    for lang in word_counts.keys():
        word2id[lang] = dict()
        id2word[lang] = []
        wc_by_id[lang] = []
        pd_by_id[lang] = []
        current_id = 0
        for word, count in word_counts[lang]:
            word2id[lang][word] = current_id
            id2word[lang].append(word)
            wc_by_id[lang].append(count)
            pd_by_id[lang].append([fun2id[fun] for fun in possibility_dicts[lang][word]])
            current_id = current_id+1

    return wc_by_id, pd_by_id, id2word, word2id, id2fun, fun2id



def em_algorithm(word_counts,
                 probs,
                 word_probs,
                 word_possibilities,
                 convergence_threshold=1e-5):
    """ The actual algorithm
    
    
    :param word_counts: dict of list of ints, has word idpossibilities coded as IDs
    :type  occurrence_tuples: [([int],int)] 
    :param init_probs: np.[double]
    :param convergence_threshold: double
    :returns: np.[double]
    """
    langs = word_counts.keys()
    convergence_diff = convergence_threshold
    total_counts = 0
    total_counts = sum([count for counts in word_counts.values() for count in counts])
    expected_counts = dict()
    expected_fun_counts = dict()
    for lang in langs:
        expected_counts[lang] = [np.zeros([len(poss)]) for poss in word_possibilities[lang]]
    while convergence_diff >= convergence_threshold:
        #Expectation
        expected_fun_counts_tot = np.zeros([probs.size])
        for s in langs:
            expected_fun_counts[s] = np.zeros([probs.size])
            for i in range(len(word_counts[s])):
                joint_probs = word_probs[s][i]*probs[word_possibilities[s][i]]
                fun_probs = joint_probs/np.sum(joint_probs)
                expected_counts[s][i]=word_counts[s][i]*fun_probs
                expected_fun_counts[s][word_possibilities[s][i]]=\
                    expected_fun_counts[s][word_possibilities[s][i]]+expected_counts[s][i]
            expected_fun_counts_tot = expected_fun_counts_tot + expected_fun_counts[s]
        #Maximization
        new_probs = expected_fun_counts_tot

        for s in langs:
            for i in range(len(word_counts[s])):
                word_probs[s][i] = expected_counts[s][i]/expected_fun_counts[s][word_possibilities[s][i]]

        #Termination criteria
        prob_quotients = new_probs / probs
        threshold_mask = np.abs(prob_quotients) > 1e-50*total_counts    # used for numpy advanced indexing to remove differences
                                                                # caused by numerical imprecision
        convergence_diff = np.sum(new_probs[threshold_mask]*np.log(prob_quotients[threshold_mask]))/total_counts
        probs = new_probs
        #print(convergence_diff)
    return probs/total_counts, word_probs