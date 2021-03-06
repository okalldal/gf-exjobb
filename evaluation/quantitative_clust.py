from trainomatic import trainomatic
from collections import defaultdict
from itertools import product, groupby, islice
from utils import read_probs, Word
from numpy import log
import logging 
import sys
import random
from nltk.corpus import wordnet as wn
from argparse import ArgumentParser
from os.path import basename, splitext
import models
import clust

def read_poss_dict(path):
    with open(path, encoding='utf-8') as f:
        # format: 
        #    columnist \t NOUN \t columnistFem_N \t columnistMasc_N
        lines = (l.strip().split('\t') for l in f)
        return defaultdict(lambda: [], {Word(l[0].lower(), l[1].lower()): l[2:] for l in lines})

def reverse_poss_dict(poss_dict_path):
    out = dict()
    with open(poss_dict_path, encoding='utf-8') as f:
        lines = (l.strip().split('\t') for l in f)
        for c in lines:
            for fun in c[2:]:
                if fun in out:
                    out[fun].append(Word(c[0].lower(), c[1].lower()))
                else:
                    out[fun] = [Word(c[0].lower(), c[1].lower())]
    return out

def get_bigrams_for_lemmas(lemmas, tree):
    bigrams = [w for w in get_bigrams(tree) 
               if w[0].lemma in lemmas or w[1].lemma in lemmas]
    return list(set(bigrams))


def get_bigrams(tree):
    for w in tree:
        dep = Word(w.lemma, w.upostag)
        head = Word(tree[w.head].lemma, tree[w.head].upostag)
        yield (dep, head, w.deprel)


def possible_bigrams(bigrams, possdict, deprel, max_perms=1000):
    vocab = set()
    vocab.update(w[0] for w in bigrams if not w[0].is_root and possdict[w[0]])
    vocab.update(w[1] for w in bigrams if not w[1].is_root and possdict[w[1]])
    reduced_dict = [[(w, poss) for poss in possdict[w]] for w in vocab]
    permutations = product(*reduced_dict)
    out = []
    for i, replacements in enumerate(permutations):
        if i > max_perms:
            return None
        swapdict = dict(replacements) # swap word for abstract function
        swap = lambda w: swapdict[w] if w in vocab else w.lemma # Don't swap 'ROOT' etc
        if not deprel:
            yield [(swap(w), swap(h)) for w, h, rel in bigrams]
        else:
            yield [(swap(w), swap(h), rel) for w, h, rel in bigrams]


def bigrams_prob(bigrams, pos, probs):
    prob = 0
    total = 0
    for bigram in bigrams:
        try:
            p = probs.get(bigram, pos)
            if not p == 0:
                prob += -log(p)
                total += 1
        except ValueError:
            continue
    if total == 0: 
        return 0
    else:
        return prob/total


def read_wnid2fun(path):
    with open(path, encoding='utf-8') as f:
        for l in f:
            l_split = l.split()
            if len(l_split)==0 or l_split[0]!= 'fun':
                continue
            fun = l_split[1]
            l_splitbar = l.split('--')
            if len(l_splitbar)<2:
                continue
            try:
                wnid = int(l_splitbar[1].split()[0])
                yield wnid, fun
            except ValueError:
                continue


def run(trees, use_deprel, probs, possdict, linearize, wn2fun):
    total = 0
    no_error = 0
    success = 0
    top_success = 0
    random_success = 0
    prob_not_found = 0
    unambig = 0

    data_error = 0
    parse_error = 0
    lemma_error = 0
    overflow_error = 0

    for i, (wnid, tree) in enumerate(trees):

        total += 1

        if i % 5000 == 0:
            logging.info('i={}'.format(i))

        wnfun = wn2fun[wnid]
        fun = clust.Cluster(wnfun).cluster
        if not fun:
            # wnid not found
            data_error += 1
            continue
        
        try:
            lemmas = [w.lemma for w in linearize[fun]]
        except KeyError:
            # cant linearize function
            data_error += 1
            continue

        try:
            lemma = next(w.lemma for w in tree if w.lemma in lemmas)
        except:
            # didnt find the lemma in the tree
            lemma_error + 1
            continue

        if lemmas and all(w.upostag.lower() != 'noun' for w in tree if w.lemma in lemmas):
            # UD parsed data failed
            parse_error += 1
            continue
        
        if sum(len(possdict[l]) for l in linearize[fun]) == len(lemmas):
            # lemma not ambigiuous
            unambig += 1

        bigrams = get_bigrams_for_lemmas(lemmas, tree)

        pos = [(n.upostag, h.upostag) for n,h,r in bigrams]
        
        poss_bigrams = list(possible_bigrams(bigrams, possdict,
            deprel=use_deprel))
        
        if not poss_bigrams:
            overflow_error += 1
            continue

        if len(poss_bigrams) <= 1:
            unambig += 1

        # no errors
        no_error += 1

        rank = [(bigrams_prob(b, p, probs), b) 
                for b, p in zip(poss_bigrams, pos)]
        is_ambig = len(rank) > 1
        rank = sorted(rank, key=lambda x: x[0])
       
        
        p_rand, b_rand = random.choice(rank)
        p, top  = next(groupby(rank, lambda x: x[0]))
        top = [el for el in top]
        check = lambda w: w and clust.Cluster(w).top_synset(lemma) == wnfun
        in_oracle  = any(any(check(w[0]) or check(w[1]) for w in b) for p, b in top)
        in_top = any(check(w[0]) or check(w[1]) for w in random.choice(top)[1])
        in_rand = any(check(w[0]) or check(w[1]) for w in b_rand) 

        if p == 0:
            prob_not_found += 1
        else:
            if in_oracle:
                success += 1
            if in_top:
                top_success += 1
            if in_rand:
                random_success += 1

    print(('total: {}, no error: {}, success oracle: {}, success top: {}, success random: {}, ' 
        'prob_not_found: {}, unambig: {}, overflow error: {}, lemma error: {}, data error: {}, '
        'parse error: {}')
        .format(total, no_error, success, top_success, random_success, prob_not_found, 
            unambig, overflow_error, lemma_error, data_error, parse_error))

# ProbDictionary with same interface as the ProbDatabase
class ProbDict():
    def __init__(self, filename):
        self.d = read_probs(filename)
    
    def get(self, key):
        try:
            return self.d[key]
        except KeyError:
            return 0

    def close(self):
        del self.d

def init(args):
    logging.basicConfig(level=logging.INFO)
    logging.info('Loading Probabilities')
    tablename = splitext(basename(args.probs))[0]
    if args.deprel:
        probs = models.BigramDeprel(args.database, tablename)
        #probs = models.InterpolationDeprel(args.database, tablename)
    else:
        probs = models.Bigram(args.database, tablename)
        # probs = models.Interpolation(args.database, tablename)
    possdict = read_poss_dict(path=args.possdict)
    linearize = reverse_poss_dict(args.possdict)
    wn2fun = defaultdict(lambda: None, {s.offset(): s.name() for s in wn.all_synsets()})
    clust.init_dicts(args.dict)
    logging.info('Initialization finished')

    return probs, possdict, linearize, wn2fun


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--possdict', 
        nargs='?',
        default='../data/possibility_dictionaries/wn/eng.txt'
    )
    parser.add_argument('--dict', '-d',
        choices=['wn_clust', 'super_clust'],
        default='wn_clust'
    )
    parser.add_argument('--deprel',
        action='store_true'
    )
    parser.add_argument('--probs',
        nargs='?',
        default='../results/kras_udgold_nodep.cnt'
    )
    parser.add_argument('--sentence-data',
        nargs='?',
        default='example_data/test_en.conllu'
    )
    parser.add_argument('--sentence-answer',
        nargs='?',
        default='example_data/test_en_egs.tsv'
    )
    parser.add_argument('--database',
        nargs='?',
        help='Use a database instead of reading the probfiles directly'
    )
    parser.add_argument('--num', '-n',
        nargs='?',
        type=int,
        default=1000
    )
    args = parser.parse_args()
    with open(args.sentence_answer) as sense:
        with open(args.sentence_data) as data:
            trees = trainomatic(data, sense)
            top = islice(trees, args.num)
            run(top, args.deprel, *init(args))
