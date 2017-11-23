from trainomatic import trainomatic
from collections import defaultdict
from itertools import product, groupby, islice
from utils import read_probs, read_poss_dict, Word, reverse_poss_dict
from numpy import log
import logging 
import sys
from nltk.corpus import wordnet as wn
from argparse import ArgumentParser

def get_bigrams_for_lemmas(lemmas, tree):
    bigrams = [(w,h) for w, h in get_bigrams(tree) 
               if w in lemmas or h in lemmas]
    return list(set(bigrams))


def get_bigrams(tree):
    return [(
             Word(w.lemma, w.upostag, w.deprel), 
             Word(tree[w.head].lemma, tree[w.head].upostag) 
                 if w.deprel != 'root' else Word('ROOT')
            ) 
            for w in tree]


def possible_bigrams(bigrams, possdict):
    vocab = set()
    vocab.update(w for w, _ in bigrams if not w.is_root and possdict[w])
    vocab.update(h for _, h in bigrams if not h.is_root and possdict[h])
    reduced_dict = [[(w, poss) for poss in possdict[w]] for w in vocab]
    permutations = product(*reduced_dict)
    out = []
    for replacements in permutations:
        swapdict = dict(replacements) # swap word for abstract function
        swap = lambda w: swapdict[w] if w in vocab else w.lemma # Don't swap 'ROOT' etc
        out.append([(swap(w), swap(h)) for w, h in bigrams])
    return out


def bigrams_prob(bigrams, probdict):
    prob = 0
    total = 0
    for bigram in bigrams:
        try:
            p = probdict[bigram]
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
    lemma_not_found = 0
    prob_not_found = 0
    success = 0
    total = 0
    ambig = 0
    ambig_total = 0

    import resource

    for i, (wnid, tree) in enumerate(trees):
        if i % 100 == 0 or i<10:
            logging.info('i={}'.format(i))

        if i % 100 == 0:
            print('Memory usage: %s (kb)' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        total += 1

        fun = wn2fun[wnid] 
        if not fun:
            continue
        lemmas = linearize[fun] 
        bigrams = get_bigrams_for_lemmas(lemmas, tree)

        if not bigrams:
            lemma_not_found += 1
            continue

        rank = [(bigrams_prob(b, probs), b) 
                for b in possible_bigrams(bigrams, possdict)]
        is_ambig = len(rank) > 1
        rank = sorted(rank, key=lambda x: x[0])
       
        if is_ambig:
            ambig_total += 1 
        
        """ FIRST 
        p, first = rank[0]
        in_top = any(w == fun or h == fun for (w, h) in first)
        """
        """ ORACLE """
        p, top = next(groupby(rank, lambda x: x[0]))
        in_top = any(any(w == fun or h == fun for w, h in b) for p, b in top)

        if p == 0:
            prob_not_found += 1
        else:
            if in_top and is_ambig:
                ambig += 1
            if in_top:
                success += 1

    print('total: {}, success: {}, total ambig: {}, ambig: {}, lemma errors: {}, prob error: {}'
        .format(total, success, ambig_total, ambig, lemma_not_found, prob_not_found))


def init(args):
    logging.basicConfig(level=logging.INFO)
    logging.info('Loading Probabilities')
    probs = defaultdict(lambda: 0, read_probs(args.probs, progress_bar=False))
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
