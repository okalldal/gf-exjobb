from nltk.corpus import wordnet as wn
from utils import read_poss_dict, Word, read_probs, reverse_poss_dict
from itertools import chain, islice
from collections import defaultdict
from argparse import ArgumentParser
from trainomatic import trainomatic_sentences
from quantitative import read_wnid2fun
import logging
import random

def run(sentences, wndict, probdict, possdict, linearize):
    total = 0
    success = 0
    lemma_error = 0 
    random_success = 0
    prob_error = 0
    for i, (wnid, sentence) in enumerate(sentences):
        total += 1
        if i % 100 == 0:
            logging.info('i={}'.format(i))

        try:
            fun = wndict[wnid]
            lemmas = linearize[fun]
        except KeyError:
            lemma_error += 1
            continue
            
        probs = (((probdict[(poss,)], poss) for poss in possdict[l]) for l in lemmas)
        rerank = list(sorted(chain(*probs), key=lambda x: x[0], reverse=True))
        p_rand, top_rand = random.choice(rerank)
        p, top = rerank[0]
        if p == 0:
            prob_error += 1
        if p > 0 and top == fun:
            success += 1
        if p > 0 and top_rand == fun:
            random_success += 1
        
    print(('total: {}, success: {}, random success: {}, lemma error: {}, prob '
        'error: {}').format(total, success,
        random_success, lemma_error, prob_error))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--probs',
        nargs='?',
        default='../results/wn_uni_udgold_nodep.cnt'
    )
    parser.add_argument('--possdict',
        nargs='?',
        default='../data/possibility_dictionaries/wn/eng.txt'
    )
    parser.add_argument('--sentence-answer',
        nargs='?',
        default='../../trainomatic/en_egs.tsv'
        #default='example_data/test_en_egs.tsv'
    )
    parser.add_argument('--dict', '-d',
        choices=['wn', 'gf'],
        default='wn'
    )
    parser.add_argument('--num', '-n',
        nargs='?',
        type=int,
        default=1000
    )
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()

    if args.v: 
        logging.basicConfig(level=logging.DEBUG)

    if args.dict == 'wn':
        wndict = {s.offset(): s.name() for s in wn.all_synsets()}
    else:
        wndict = defaultdict(lambda: None, read_wnid2fun('../data/Dictionary.gf'))

    probdict = defaultdict(lambda: 0, read_probs(args.probs))
    possdict = read_poss_dict(path=args.possdict)
    linearize = reverse_poss_dict(args.possdict)

    logging.info('loading finished')
    with open(args.sentence_answer) as sense_file:
        sentences = trainomatic_sentences(sense_file)
        top = islice(sentences, args.num)
        run(top, wndict, probdict, possdict, linearize)
