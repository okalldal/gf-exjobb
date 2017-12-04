import numpy as np
import argparse

def em_algorithm(word_counts,
                 init_counts,
                 unambiguous_counts,
                 word_probs,
                 word_possibilities,
                 convergence_threshold=1e-5):
    """
    The actual algorithm. It takes counts in the word (observed) domain and uses EM to
    give expected counts in the function (latent) domain. Words belong to one of several languages.
    Each language is represented by an integer and within one language each word is represented as
     a unique integer, counts and dictionaries for each word and language are to be given in the specified lists
     at the index corresponding to the language and words id. Each function is also represented by a unique incremented
     integer id. The possibility dictionaries for each word should contain the id:s of the functions it could represent.
     Expected counts are returned as lists with the calculated counts given at the index of each function and word's
     respective id.
    :param word_counts: list of lists of ints on the form word_counts[lang][word]
    :param init_counts: list of lists of ints on the form word_counts[lang][word]
    :param unambiguous_counts: list of numpy arrays on the form word_counts[lang][fun]
    :param word_probs: list of lists of numpy arrays on the form word_probs[lang][word]
    :param word_possibilities: list of list of numpy arrays on the form word_probs[lang][word]
    :param convergence_threshold: float
    :return: tuples with the resulting function probabilities and word counts given for each language
    """
    langs = list(range(len(word_counts)))
    convergence_diff = convergence_threshold
    total_counts = sum([count for counts in word_counts for count in counts]) + np.sum(unambiguous_counts)
    expected_counts = dict()
    expected_fun_counts = dict()
    probs = init_counts
    for lang in langs:
        expected_counts[lang] = [np.zeros([len(poss)]) for poss in word_possibilities[lang]]

    # The convergence criterion does not work for first iteration b/c of how we initiate, so make sure we run at least two iterations
    first = True
    while convergence_diff >= convergence_threshold:
        ##  Expectation
        expected_fun_counts_tot = np.zeros([probs.size]) #\sum_{si} c_{si.}, initialize here, calculate in loop
        for s in langs:
            expected_fun_counts[s] = np.zeros([probs.size]) #\sum_i c_{si.}, initialize here, calculate in loop
            for i in range(len(word_counts[s])):
                # This is the core of the algorithm where the updating of expected counts are made for each word.
                # word_possibilities[s][i] contains the function ids off all possible functions for word i in language s
                # word_probs[s][i] contains the conditional probabilities P(word|function) for word s in language i in
                # the same order the functions appear in word_possibilities[s][i]
                # in comments below the the subscript indicies always come in order: language, word, function. Dot
                # indicates the index the arrays or lists runs over, variable names are same as in thesis
                joint_probs = word_probs[s][i]*probs[word_possibilities[s][i]] #=P(Y,X) = \phi_{si.}*\pi_.
                total_prob = np.sum(joint_probs) #P(X) = \sum_k \phi_{sik}*\pi_k
                if total_prob > 0: #make sure we dont divide by zero, if sum is zero, everything is zero anyway
                    fun_probs = joint_probs/total_prob #=P(Y|X) = \phi_{si.}*\pi / (\sum_k \phi_{sik}*\pi_k
                expected_counts[s][i]=word_counts[s][i]*fun_probs #=\hat c_{si.}
                expected_fun_counts[s][word_possibilities[s][i]]=\
                    expected_fun_counts[s][word_possibilities[s][i]]+expected_counts[s][i] #\sum_i c_{si.}
            expected_fun_counts_tot = expected_fun_counts_tot + expected_fun_counts[s] #\sum_{si} c_{si.}
        ##  Maximization
        new_probs = unambiguous_counts + expected_fun_counts_tot # this is not the real probs since we don't normalize, but doesnt matter
                                            # b/c we have normalization constant in numerator denumerator in the
                                            # expression for fun_probs above

        #new_probs[new_probs < 0.001] = 0
        for s in langs:
            for i in range(len(word_counts[s])):
                with np.errstate(invalid='ignore'):
                    word_probs[s][i] = np.nan_to_num(expected_counts[s][i]/expected_fun_counts[s][word_possibilities[s][i]])

        ##  Termination criteria
        if first:
            first = False
        else:
            non_zero_probs = probs[probs>0]
            prob_quotients = new_probs[probs>0] / non_zero_probs
            convergence_diff = np.sum(non_zero_probs[prob_quotients>1e-20]*np.log(prob_quotients[prob_quotients>1e-20]))/total_counts
        probs = new_probs
    return probs, word_probs #note normalization of probs here, see comment above


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""
    Input is fed on stdin in tsv format with data for each language separated by one line consisting of only "---"
    The tsv format is: column 1: count, column 2 to f+1, the word(s) in the observed domain
    (not used but there for compatibility), column f+2 to end: the possible representations (functions) of the word
     in latent space, with each possibility consisting of p columns. A syntactic bigram with part of speech tag is
     normaly given in four columns in observed space (one for each lemma, one for each pos tag) and two columns for each
     possibility (one for each function in each possible function-bigram). When processing n-grams ALL possible
     combinations of possible latent functions should be given. Please use make_em_data.py to generate the data files 
     that feeds this script.
    """)
    parser.add_argument('-f', type=int,
                        help='Number of feature columns.',
                        default=4)
    parser.add_argument('-p', type=int, help='Number of columns per possibility', default=2)
    args = parser.parse_args()

    import sys

    if sys.stdin.__next__().strip('\n') != '---':
        print('Input must start with ---', file=sys.stderr)
        exit(1)

    # These lists index over all languages
    word_counts = list()
    word_possibilities=list()
    word_probabilities=list()

    # These are used to convert the functions to unique integer ID:s
    fun2id = dict()
    id2fun = list()
    current_id = 0

    # These lists go over all words in one language
    wc = list() # counts
    wp = list() # possibilities (dictionary)
    wprob = list() # conditional word probabilities (phi in the report), P(word|function)
    unambiguous_counts = list() # goes over all functions, used for unambiguous words to optimize processing in em algorithm
    for l in sys.stdin:
        if l.strip('\n') == '---': #new language
            # append data for this language to the data-by-language lists and reinitialize
            word_counts.append(wc)
            word_possibilities.append(wp)
            word_probabilities.append(wprob)
            wc = list()
            wp = list()
            wprob = list()
        else:
            l_split = l.strip('\n').split('\t')

            if len(l_split)==(1+args.f+args.p): # word is unambiguous
                fun = tuple(l_split[1+args.f:])
                if fun not in fun2id.keys(): # first time we see this function so give it an id
                    id2fun.append(fun)
                    fun2id[fun] = current_id
                    current_id = current_id + 1
                    unambiguous_counts.append(int(l_split[0]))
                else:
                    unambiguous_counts[fun2id[fun]] = unambiguous_counts[fun2id[fun]] + int(l_split[0])
            else: # word is ambiguous
                funs = list()
                wc.append(int(l_split[0]))
                for i in range(0, len(l_split)-(1+args.f), args.p): # for each possible function
                    fun = tuple(l_split[1+args.f+i:1+args.f+i+args.p])
                    if fun not in fun2id.keys(): # first time we see this function so give it an id
                        id2fun.append(fun)
                        fun2id[fun] = current_id
                        current_id = current_id + 1
                        unambiguous_counts.append(0)
                    funs.append(fun2id[fun])
                wp.append(np.array(funs))
                wprob.append(np.ones([len(funs)]))

    # append data for the last language to the data-by-language lists and reinitialize delete the mapping from fun to id
    #  to save memory
    word_counts.append(wc)
    word_possibilities.append(wp)
    word_probabilities.append(wprob)
    del(fun2id)

    unambiguous_counts = np.array(unambiguous_counts)
    # initialize starting probabilities for em algorithm uniformly
    init_probs = np.ones([len(id2fun)])# + np.random.uniform([len(id2fun)])/10
    em_probs, _ = em_algorithm(word_counts,
                 init_probs,
                 unambiguous_counts,
                 word_probabilities,
                 word_possibilities,
                 convergence_threshold=1e-5)
    for fun, probability in zip(id2fun, np.nditer(em_probs, order='C')):
        print(*([probability] + list(fun)), sep='\t')

