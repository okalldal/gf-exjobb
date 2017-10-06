import pgf
import sys
from itertools import takewhile, repeat
from collections import defaultdict
from ast import literal_eval
from scipy import log
from utils import Memoize, read_probs
import logging


@Memoize
def gf_labels():
    with open('../data/Lang.labels') as f:
        rows = [l.strip().split() for l in f if l.strip() != '']
    labels = defaultdict(lambda: ['head'])
    for row in rows:
        fun, *rest = row
        args = takewhile(lambda w: w[0:2] != '--', rest)
        labels[fun] = list(args)
    return labels


def find_heads(expression, prev_heads = [], label='root'):
    labels = gf_labels()
    fun, arguments = expression.unpack()
    arg_labels = labels[fun]
    headi = arg_labels.index('head')
    if (len(arguments) <= headi):
        return [(fun, prev_heads, label)], fun
    else:
        out, head = find_heads(arguments[headi], prev_heads, label)
        for i, arg in enumerate(arguments):
            if i != headi:
                cur_label = arg_labels[i] if len(arg_labels) > i else label
                tuples, _ = find_heads(arg, [head] + prev_heads, cur_label)
                out.extend(tuples)
        return out, head


def tree_prob(tree_tuples, probs):
    
    total = 0
    marginal_head = Memoize(lambda fun: sum(p for (a, b), p in probs.items() if b == fun))
    marginal_child = Memoize(lambda fun: sum(p for (a, b), p in probs.items() if a == fun))

    bigram_count = 0
    unigram_count = 0
    for node, heads in tree_tuples:
        head = heads[0] if len(heads) > 0 else 'root'
        bigram_prob = probs[(node, head)]
        unigram_prob = marginal_child(node)

        if bigram_prob != 0:
            bigram_count += 1
            prob = log(bigram_prob) - log(marginal_head(head))
        elif unigram_prob != 0:
            unigram_count += 1
            prob = log(unigram_prob)
        else:
            prob = 0

        total = total-prob

    msg = 'Generated tree probability with %d bigrams and %d unigrams'
    logging.info(msg % (bigram_count, unigram_count))
    return total


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    
    en_probs = defaultdict(lambda: 0, read_probs('../results/bigram_Eng.probs'))
    total_probs = defaultdict(lambda: 0, read_probs('../results/bigram_total.probs'))

    gr = pgf.readPGF('../data/TranslateEngSwe.pgf')
    eng = gr.languages['TranslateEng']
    swe = gr.languages['TranslateSwe']
    
    sentence = sys.argv[1] if len(sys.argv) == 2 else \
        "the horse likes to eat the hay which we all had selected" 
    print(sentence)
    print('GF\t\tEnglish\t\tTotal')
    for i, (p, ex) in enumerate(eng.parse(sentence)):
        tuples, _ = find_heads(ex)
        bigrams = [(n, hs) for n, hs, l in tuples]
        rerank_en = tree_prob(bigrams, en_probs)
        rerank_total = tree_prob(bigrams, total_probs)
        print(str(p) + '\t\t' + str(rerank_en) + '\t\t' + str(rerank_total))
        if i > 20:
            break
