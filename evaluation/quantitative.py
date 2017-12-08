from trainomatic import trainomatic
from collections import defaultdict
from itertools import product, groupby, islice
from utils import read_probs, read_poss_dict, Word, reverse_poss_dict
from database import ProbDatabase
from numpy import log
import logging 
import sys
import random
from nltk.corpus import wordnet as wn
from argparse import ArgumentParser
from os.path import basename, splitext

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
        is_valid = lambda w: w.is_root or w in vocab
        if not deprel:
            out.append([(swap(w), swap(h)) for w, h, rel in bigrams if
                is_valid(w) and is_valid(h)])
        else:
            out.append([(swap(w), swap(h), rel) for w, h, rel in bigrams if
                is_valid(w) and is_valid(h)])
    return out


def bigrams_prob(bigrams, probs):
    prob = 0
    total = 0
    for bigram in bigrams:
        try:
            p = probs.get(bigram)
            if not p == 0:
                prob += -log(p)
                total += 1
        except KeyError:
            pass
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


def wordnet_examples(pos_filter=None):
    for s in wn.all_synsets():
        if not pos_filter or s.pos() == pos_filter:
            for ex in s.examples():
                yield (s.offset(), ex)


def run(trees, use_deprel, probs, possdict, linearize, wn2fun):
    total = 0
    no_error = 0
    success = 0
    top_success = 0
    random_success = 0
    prob_not_found = 0

    data_error = 0
    parse_error = 0
    unambig_error = 0
    lemma_error = 0
    overflow_error = 0

    for i, (wnid, tree) in enumerate(trees):

        total += 1

        if i % 5000 == 0:
            logging.info('i={}'.format(i))

        fun = wn2fun[wnid] 
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

        if not [w for w in tree if w.lemma in lemmas]:
            # didnt find the lemma in the tree
            lemma_error += 1
            continue

        if lemmas and all(w.upostag.lower() != 'noun' for w in tree if w.lemma in lemmas):
            # UD parsed data failed
            parse_error += 1
            continue
        
        if sum(len(possdict[l]) for l in linearize[fun]) == len(lemmas):
            # lemma not ambigiuous
            unambig_error += 1
            continue

        bigrams = get_bigrams_for_lemmas(lemmas, tree)

        poss_bigrams = possible_bigrams(bigrams, possdict, deprel=use_deprel)
        
        if not poss_bigrams:
            overflow_error += 1
            continue

        if len(poss_bigrams) <= 1:
            unambig_error += 1
            continue

        # no errors
        no_error += 1

        rank = [(bigrams_prob(b, probs), b) 
                for b in poss_bigrams]
        is_ambig = len(rank) > 1
        rank = sorted(rank, key=lambda x: x[0])
       
        
        """ FIRST 
        p, first = rank[0]
        in_top = any(w == fun or h == fun for (w, h) in first)
        """
        """ ORACLE """
        p_rand, b_rand = random.choice(rank)
        p, top  = next(groupby(rank, lambda x: x[0]))
        top = [el for el in top]
        in_oracle  = any(any(w[0] == fun or w[1] == fun for w in b) for p, b in top)
        in_top = any(w[0] == fun or w[1] == fun for w in random.choice(top)[1])
        in_rand = any(w[0] == fun or w[1] == fun for w in b_rand) 

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
        'prob_not_found: {}, overflow error: {}, lemma error: {}, data error: {}, '
        'unambig error: {}, parse error: {}')
        .format(total, no_error, success, top_success, random_success, prob_not_found, 
            overflow_error, lemma_error, data_error, unambig_error, parse_error))

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
    if args.database:
        tablename = splitext(basename(args.probs))[0]
        probs = ProbDatabase(args.database, tablename)
    else:
        probs = ProbDict(args.probs)
    possdict = read_poss_dict(path=args.possdict)
    linearize = reverse_poss_dict(args.possdict)
    if args.dict == 'gf':
        wn2fun = defaultdict(lambda: None, read_wnid2fun('../data/Dictionary.gf'))
    elif args.dict == 'wn':
        wn2fun = defaultdict(lambda: None, {s.offset(): s.name() for s in wn.all_synsets()})
    logging.info('Initialization finished')

    return probs, possdict, linearize, wn2fun


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--possdict', 
        nargs='?',
        default='../data/possibility_dictionaries/wn/eng.txt'
    )
    parser.add_argument('--dict', '-d',
        choices=['wn', 'gf'],
        default='wn'
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
