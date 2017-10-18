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


def tree_prob(tree_tuples, bigramprobs, unigramprobs):
    
    total = 0

    bigram_count = 0
    unigram_count = 0
    for node, heads in tree_tuples:
        head = heads[0] if len(heads) > 0 else 'ROOT'
        bigram_prob = bigramprobs[(node, head)]
        unigram_prob = unigramprobs[node]

        if bigram_prob != 0:
            print("({},{}): {}".format(node, head, bigram_prob))
            bigram_count += 1
            prob = log(bigram_prob) - log(unigramprobs[head])
        elif unigram_prob != 0:
            print("({},): {}".format(node, unigram_prob))
            unigram_count += 1
            prob = log(unigram_prob)
        else:
            print("{} no collected data".format(node))
            prob = 0

        total = total-prob

    msg = 'Generated tree probability with %d bigrams and %d unigrams'
    logging.info(msg % (bigram_count, unigram_count))
    return total

def run(sentence, grammar, bigramprobs, unigramprobs):
    eng = grammar.languages['TranslateEng']
    swe = grammar.languages['TranslateSwe']
    
    print(sentence)
    print('GF\t\tUs\t\tTotal\t\tTranslation')
    for i, (p, ex) in enumerate(eng.parse(sentence)):
        tuples, _ = find_heads(ex)
        bigrams = [(n, hs) for n, hs, l in tuples]
        rerank_total = tree_prob(bigrams, bigramprobs, unigramprobs)
        print(str(p) + '\t\t' +  str(rerank_total) + '\t\t' + str(p+rerank_total) +'\t\t' + swe.linearize(ex))
        if i > 10:
            break


def init():
    # unigram
    with open('../results/prasanth_counts_total_unigram.probs') as f:
        data = (l.strip().split('\t') for l in f)
        unigramprobs = defaultdict(lambda: 0, ((t, float(p)) for (t, p) in data))
    # bigram
    # filter out non bigram probabilities, sometimes we get these
    bigramprobs = defaultdict(lambda: 0, ((t, p) for (t, p) in read_probs('../results/prasanth_counts_total.probs') 
                                           if len(t) == 2 ))
    # GF
    grammar = pgf.readPGF('../data/TranslateEngSwe.pgf')
    return grammar, bigramprobs, unigramprobs


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    sentence = sys.argv[1] if len(sys.argv) == 2 else \
        "he works at the bank" 
    # bigramprobs, unigramprobs = probs()
    # run(sentence, gr, bigramprobs, unigramprobs)