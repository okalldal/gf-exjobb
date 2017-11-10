import numpy as np
import logging
import argparse

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
    return probs, word_probs #note normalization of probs here, see comment above


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
    unambiguous_counts = np.array(unambiguous_counts)
    init_probs = np.ones([len(id2fun)])# + np.random.uniform([len(id2fun)])/10
    em_probs, _ = em_algorithm(word_counts,
                 init_probs,
                 unambiguous_counts,
                 word_probabilities,
                 word_possibilities,
                 convergence_threshold=1e-5)
    for fun, probability in zip(id2fun, np.nditer(em_probs, order='C')):
        print(*([probability] + list(fun)), sep='\t')

