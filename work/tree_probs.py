import pgf
import sys
from itertools import takewhile
from collections import defaultdict
from ast import literal_eval
from scipy import log
import logging

def gf_labels():
    with open('../data/Lang.labels') as f:
        rows = [l.strip().split() for l in f if l.strip() != '']
    labels = defaultdict(lambda: ['head'])
    for row in rows:
        fun, *rest = row
        args = takewhile(lambda w: w[0:2] != '--', rest)
        labels[fun] = list(args)
    return labels

labels = gf_labels()

def read_probs(path):
    with open(path) as f:
        probs = [tuple(line.strip().split('\t')) for line in f]
        parse_line = lambda line: (literal_eval(line[0]), float(line[1]))
        probs = defaultdict(lambda: 0, map(parse_line, probs))
    return probs


def gen_bigrams(expression, prev_head, label):
    """Generate bigrams with labels from a gf expression."""
    fun, args = expression.unpack()
    #logging.debug('fun: ' + str(fun))
    headi = labels[fun].index('head')
    if (len(args) <= headi):
        return [(fun, prev_head, label)], fun
    else:
        out, head = gen_bigrams(args[headi], prev_head, label)
        for i, arg in enumerate(args):
            if i != headi:
                tuples, _ = gen_bigrams(arg, head, labels[fun][i])
                out.extend(tuples)
        #logging.debug('out: ' + str(out))
        return out, head


class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}
    def __call__(self, *args):
        if not args in self.memo:
            self.memo[args] = self.f(*args)
        return self.memo[args]


def tree_prob(tree_tuples, probs):
    
    total = 0
    marginal_head = Memoize(lambda fun: sum(p for (a, b), p in probs.items() if b == fun))
    marginal_child = Memoize(lambda fun: sum(p for (a, b), p in probs.items() if a == fun))

    for node, head in tree_tuples:

        logging.debug((node, head))
        bigram_prob = probs[(node, head)]
        unigram_prob = marginal_child(node)

        if bigram_prob != 0:
            logging.debug('bigram / marginal ' + str(bigram_prob / marginal_head(head)))
            prob = log(bigram_prob) - log(marginal_head(head))
        elif unigram_prob != 0:
            logging.debug('unigram ' + str(unigram_prob))
            prob = log(unigram_prob)
        else:
            logging.debug('ignored')
            prob = 0

        total = total-prob

    return total


if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    bigram_probs = read_probs('../results/bigram_Eng.probs')

    gr = pgf.readPGF('../data/TranslateEngSwe.pgf')
    eng = gr.languages['TranslateEng']
    swe = gr.languages['TranslateSwe']
    
    sentence = sys.argv[1] if len(sys.argv) == 2 else "the horse likes to eat hay" 

    print('GF\t\t\tUs')
    for i, (p, ex) in enumerate(eng.parse(sentence)):
        tuples, _ = gen_bigrams(ex, 'root', 'root')
        bigrams = [(a, b) for a, b, c in tuples]
        rerank = tree_prob(bigrams, bigram_probs)
        print(str(p) + '\t\t\t' + str(rerank))
        if i > 100:
            break
