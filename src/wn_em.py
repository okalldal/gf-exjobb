import numpy as np

def em_algorithm(word_counts,
                 init_fun_counts,
                 unambiguous_counts,
                 init_expected_wordfun_probs,
                 word_possibilities,
                 convergence_threshold=1e-5):
    langs = list(range(len(word_counts)))
    total_counts = sum([count for counts in word_counts for count in counts]) + np.sum(unambiguous_counts)
    expected_fun_counts = init_fun_counts
    wordfun_probs = init_expected_wordfun_probs
    first = True
    while True:
        new_expected_fun_counts_lang = [np.zeros([init_fun_counts.size]) for lang in range(len(word_counts))] #\sum_{si} c_{si.}, initialize here, calculate in loop
        new_expected_fun_counts = np.zeros([init_fun_counts.size]) #\sum_{si} c_{si.}, initialize here, calculate in loop
        new_expected_wordfun_counts = list() 
        for s in range(len(word_counts)):
            wfcounts = list()
            for i in range(len(word_counts[s])):
                joint_count = wordfun_probs[s][i]*expected_fun_counts[word_possibilities[s][i]] #=P(Y,X) = \phi_{si.}*\pi_.
                word_count = np.sum(joint_count) #=P(X) = \phi_{si.}*\pi / (\sum_k \phi_{sik}*\pi_k
                wfc=word_counts[s][i]*joint_count/word_count #=\hat c_{si.}
                wfcounts.append(wfc)
                new_expected_fun_counts_lang[s][word_possibilities[s][i]]=\
                    new_expected_fun_counts_lang[s][word_possibilities[s][i]]+wfc
            new_expected_wordfun_counts.append(wfcounts)
            new_expected_fun_counts[word_possibilities[s][i]]=\
                new_expected_fun_counts[word_possibilities[s][i]]+new_expected_fun_counts_lang[s][word_possibilities[s][i]]
        new_expected_fun_counts = unambiguous_counts + new_expected_fun_counts
        for s in range(len(word_counts)):
            for i in range(len(word_counts[s])):
                wordfun_probs[s][i] = new_expected_wordfun_counts[s][i]/new_expected_fun_counts_lang[s][word_possibilities[s][i]]
        ##  Termination criteria
        if first:
            first = False
        else:
            prob_quotients = new_expected_fun_counts/expected_fun_counts
            threshold_mask = prob_quotients > 1e-30    # used to remove differences caused by numerical imprecision
            convergence_diff = np.sum(new_expected_fun_counts[threshold_mask]*np.log(prob_quotients[threshold_mask]))/total_counts
            if convergence_diff < convergence_threshold:
                break
        ## Pruning of low prob functions
        threshold_mask = new_expected_fun_counts < 0.1
        new_expected_fun_counts[threshold_mask]=0

        expected_fun_counts=new_expected_fun_counts
        expected_wordfun_counts = new_expected_wordfun_counts
        print(expected_fun_counts)
    return new_expected_fun_counts


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Read a tsv file where first column is a count the next -f columns are the feature name and the rest of the columns are possibilitie. Each possibility is -p columns long. Multiple languages are separated with one line consisting of the characters '---'.")
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

    fun2id = dict()
    id2fun = list()
    current_id = 0

    wc = list()
    wp = list()
    unambiguous_counts = list()
    for l in sys.stdin:
        if l.strip('\n') == '---': #new language
            word_counts.append(wc)
            word_possibilities.append(wp)
            wc = list()
            wp = list()
            wprob = list()
        else:
            l_split = l.strip('\n').split('\t')

            if len(l_split)==(1+args.f+args.p): #unambiguous
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


    word_counts.append(wc)
    word_possibilities.append(wp)
    del(wc)
    del(wp)
    del(fun2id)
    unambiguous_counts = np.array(unambiguous_counts)

    init_fun_counts = np.ones([len(id2fun)])
    init_word_counts = [[np.ones([len(word)]) for word in lang] for lang in word_possibilities]
    em_probs = em_algorithm(word_counts,
                 init_fun_counts,
                 unambiguous_counts,
                 init_word_counts,
                 word_possibilities,
                 convergence_threshold=1e-5)
    for fun, probability in zip(id2fun, np.nditer(em_probs, order='C')):
        print(*([probability] + list(fun)), sep='\t')

