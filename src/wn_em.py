import numpy as np
import logging
import argparse

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
    starting_probs = np.ones([len(id2fun)]) / len(id2fun)
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
        probabilities[fun]=float(prob)
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
        oov_words = 0
        for word, count in word_counts[lang]:
            if word in possibility_dicts[lang].keys():
                word2id[lang][word] = current_id
                id2word[lang].append(word)
                wc_by_id[lang].append(count)
                pd_by_id[lang].append([fun2id[fun] for fun in possibility_dicts[lang][word]])
                current_id = current_id+1
            else:
                oov_words = oov_words + 1
        if oov_words>0:
            logging.debug('found {} oov words in counts for {}.'.format(oov_words,lang))
    return wc_by_id, pd_by_id, id2word, word2id, id2fun, fun2id



def em_algorithm(word_counts,
                 init_counts,
                 unambiguous_counts,
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
    langs = list(range(len(word_counts)))
    convergence_diff = convergence_threshold
    total_counts = sum([count for counts in word_counts for count in counts]) + np.sum(unambiguous_counts)
    expected_counts = dict()
    expected_fun_counts = dict()
    probs = init_counts
    for lang in langs:
        expected_counts[lang] = [np.zeros([len(poss)]) for poss in word_possibilities[lang]]
    first = True
    while convergence_diff >= convergence_threshold:
        ##  Expectation
        expected_fun_counts_tot = np.zeros([probs.size]) #\sum_{si} c_{si.}, initialize here, calculate in loop
        for s in langs:
            expected_fun_counts[s] = np.zeros([probs.size]) #\sum_i c_{si.}, initialize here, calculate in loop
            for i in range(len(word_counts[s])):
                #print(word_possibilities[s][i], file=sys.stderr)
                joint_probs = word_probs[s][i]*probs[word_possibilities[s][i]] #=P(Y,X) = \phi_{si.}*\pi_.
                fun_probs = joint_probs/np.sum(joint_probs) #=P(Y|X) = \phi_{si.}*\pi / (\sum_k \phi_{sik}*\pi_k
                expected_counts[s][i]=word_counts[s][i]*fun_probs #=\hat c_{si.}
                expected_fun_counts[s][word_possibilities[s][i]]=\
                    expected_fun_counts[s][word_possibilities[s][i]]+expected_counts[s][i] #\sum_i c_{si.}
            expected_fun_counts_tot = expected_fun_counts_tot + expected_fun_counts[s] #\sum_{si} c_{si.}
        ##  Maximization
        new_probs = unambiguous_counts + expected_fun_counts_tot # this is not the real probs since we don't normalize, but doesnt matter
                                            # b/c we have normalization constant in numerator denumerator in the
                                            # expression for fun_probs above

        for s in langs:
            for i in range(len(word_counts[s])):
                word_probs[s][i] = expected_counts[s][i]/expected_fun_counts[s][word_possibilities[s][i]]

        ##  Termination criteria
        if first:
            first = False
        else:
            prob_quotients = new_probs / probs
            threshold_mask = np.abs(prob_quotients) > 1e-50*total_counts    # used for numpy advanced indexing to remove differences
                                                                    # caused by numerical imprecision
            convergence_diff = np.sum(new_probs[threshold_mask]*np.log(prob_quotients[threshold_mask]))/total_counts
        probs = new_probs
        #print(convergence_diff)
    return probs/total_counts, word_probs #note normalization of probs here, see comment above


def em_algorithm_uniform_wp(word_counts,
                 probs,
                 word_possibilities,
                 convergence_threshold=1e-5):
    """ The actual algorithm


    :param word_counts: dict of list of ints, has word idpossibilities coded as IDs
    :type  occurrence_tuples: [([int],int)]
    :param init_probs: np.[double]
    :param convergence_threshold: double
    :returns: np.[double]
    """
    langs = list(range(len(word_counts)))
    convergence_diff = convergence_threshold
    total_counts = sum([count for counts in word_counts for count in counts])
    while convergence_diff >= convergence_threshold:
        ##  Expectation
        expected_fun_counts = np.zeros([probs.size])  # \sum_{si} c_{si.}, initialize here, calculate in loop
        for s in langs:
            for i in range(len(word_counts[s])):
                possibiities = word_possibilities[s][i]
                joint_probs = probs[possibiities]  # =P(Y,X) = \phi_{si}*\pi_., omit \phi_{si} b/c will cancel out in next line
                fun_probs = joint_probs / np.sum(joint_probs)  # =P(Y|X) = \phi_{si}*\pi / (\sum_k \phi_{si}*\pi_k
                expected_counts = word_counts[s][i] * fun_probs  # =\hat c_{si.}
                expected_fun_counts[possibiities] = \
                    expected_fun_counts[possibiities] + expected_counts  # \sum_si c_{si.}
        ##  Maximization
        new_probs = expected_fun_counts  # this is not the real probs since we don't normalize with |F|, but doesnt matter
        # b/c we have normalization constant in numerator denumerator in the
        # expression for fun_probs above

        ##  Termination criteria
        prob_quotients = new_probs / probs
        threshold_mask = np.abs(
            prob_quotients) > 1e-50 * total_counts  # used for numpy advanced indexing to remove differences
        # caused by numerical imprecision
        convergence_diff = np.sum(new_probs[threshold_mask] * np.log(prob_quotients[threshold_mask])) / total_counts
        probs = new_probs
        # print(convergence_diff)
    return probs / total_counts  # note normalization of probs here, see comment above

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=int,
                        help='Number of feature columns.',
                        default=4)
    parser.add_argument('-p', type=int, help='Number of columns per possibility', default=2)
    args = parser.parse_args()

    import sys

    if sys.stdin.__next__().strip('\n') != '---':
        print('Input must start with ---', file=sys.stderr)
        exit(1)

    word_counts = list()
    word_possibilities=list()
    word_probabilities=list()

    fun2id = dict()
    id2fun = list()
    current_id = 0

    wc = list()
    wp = list()
    wprob = list()
    unambiguous_counts = list()
    for l in sys.stdin:
        if l.strip('\n') == '---': #new language
            word_counts.append(wc)
            word_possibilities.append(wp)
            word_probabilities.append(wprob)
            wc = list()
            wp = list()
            wprob = list()
        else:
            l_split = l.strip('\n').split('\t')

            if len(l_split)==(1+args.f+args.p):
                fun = tuple(l_split[1+args.f:])
                if fun not in fun2id.keys():
                    id2fun.append(fun)
                    fun2id[fun] = current_id
                    current_id = current_id + 1
                    unambiguous_counts.append(int(l_split[0]))
                else:
                    unambiguous_counts[fun2id[fun]] = unambiguous_counts[fun2id[fun]] + int(l_split[0])
            else:
                funs = list()
                wc.append(int(l_split[0]))
                for i in range(0, len(l_split)-(1+args.f), args.p):
                    fun = tuple(l_split[1+args.f+i:1+args.f+i+args.p])
                    if fun not in fun2id.keys():
                        id2fun.append(fun)
                        fun2id[fun] = current_id
                        current_id = current_id + 1
                        unambiguous_counts.append(0)
                    funs.append(fun2id[fun])
                wp.append(np.array(funs))
                wprob.append(np.ones([len(funs)])/(len(funs)))


    word_counts.append(wc)
    word_possibilities.append(wp)
    word_probabilities.append(wprob)
    del(wc)
    del(wp)
    del(wprob)
    del(fun2id)
    unambiguous_counts = np.array(unambiguous_counts)+np.ones([len(id2fun)])
    init_probs = np.ones([len(id2fun)])# + np.random.uniform([len(id2fun)])/10
    em_probs, _ = em_algorithm(word_counts,
                 init_probs,
                 unambiguous_counts,
                 word_probabilities,
                 word_possibilities,
                 convergence_threshold=1e-5)
    for fun, probability in zip(id2fun, np.nditer(em_probs, order='C')):
        print(*([probability] + list(fun)), sep='\t')

