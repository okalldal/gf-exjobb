from nltk.corpus import wordnet as wn
from utils import Word, read_probs
from itertools import chain, islice, groupby
from collections import defaultdict
from argparse import ArgumentParser
from trainomatic import trainomatic
from quantitative import read_wnid2fun
from os.path import basename, splitext
import logging
import random
import models

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

def run(trees, probs, possdict, linearize, wn2fun):
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

        unigrams = list(chain(*[possdict[l] for l in linearize[fun]]))

        if len(unigrams) <= 1:
            unambig_error += 1
            continue

        # no errors
        no_error += 1

        rank = [(probs.log((unigram,)), unigram) 
                for unigram in unigrams]
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
        in_oracle  = any(b==fun for p, b in top)
        in_top = random.choice(top)[1] == fun
        in_rand = fun == b_rand 

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

def init(args):
    logging.basicConfig(level=logging.INFO)
    logging.info('Loading Probabilities')
    tablename = splitext(basename(args.probs))[0]
    probs = models.Unigram(args.database, tablename)
    possdict = read_poss_dict(path=args.possdict)
    linearize = reverse_poss_dict(args.possdict)
    if args.dict == 'gf':
        wn2fun = defaultdict(lambda: None, read_wnid2fun('../data/Dictionary.gf'))
    elif args.dict == 'wn':
        wn2fun = defaultdict(lambda: None, {s.offset(): s.name() for s in wn.all_synsets()})
    elif args.dict == 'clust':
        with open('../data/possibility_dictionaries/wn_clust.tsv') as f:
                ls = (l.strip().split('\t') for l in f)
                wn2clust = defaultdict(lambda: None, ls)
        wn2fun = defaultdict(lambda: None, 
            {s.offset(): wn2clust[s.name()] if wn2clust[s.name()] else None for
            s in wn.all_synsets()})
    logging.info('Initialization finished')

    return probs, possdict, linearize, wn2fun


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--possdict', 
        nargs='?',
        default='../data/possibility_dictionaries/gf_wn/eng.txt'
    )
    parser.add_argument('--dict', '-d',
        choices=['wn', 'clust', 'gf'],
        default='wn'
    )
    parser.add_argument('--deprel',
        action='store_true'
    )
    parser.add_argument('--probs',
        nargs='?',
        default='../results/nodep_wn_autoparsed_th50_uni.cnt'
    )
    parser.add_argument('--sentence-data',
        nargs='?',
        default='../../trainomatic/en.conllu'
    )
    parser.add_argument('--sentence-answer',
        nargs='?',
        default='../../trainomatic/en_egs.tsv'
    )
    parser.add_argument('--database',
        nargs='?',
        default='../probs.db',
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
            run(top, *init(args))
