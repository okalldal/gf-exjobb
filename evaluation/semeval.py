from utils import UDNode
from xml.dom import minidom
from nltk.corpus import wordnet as wn
import evaluation
import models
import logging
from tqdm import tqdm
from argparse import ArgumentParser

# we must read both from the udpipe parsed file and the original semeval file
# since the POS tags are different
def udpipe_data(data_file):
    ud_tree = []
    while True:
        data_line = data_file.readline()
        if not data_line:
            break
        elif data_line == '\n':
            yield ud_tree
            ud_tree = []
        elif not data_line.startswith('#'):
            try:
                ud_tree.append(UDNode(data_line))
            except ValueError:
                logging.warn('cant parse line %s' % data_line.strip())

POS = {'N': 'noun', 'V': 'verb', 'J': 'adj', 'R': 'adv'}

def semeval_data(data_file):
    xmldoc = minidom.parse(data_file)
    sentences = xmldoc.getElementsByTagName('sentence')
    for sentence in sentences:
        words = sentence.getElementsByTagName('wf')
        yield [(w.getAttribute('lemma'), w.getAttribute('pos'),
            w.getAttribute('id')) for w in words]

def combine(semeval, udpipe):
    for sentence, tree in zip(semeval, udpipe):
        i = 0
        for lemma, pos, id_name in sentence:
            if pos != 'X':
                tree[i].lemma = lemma
                tree[i].upostag = POS[pos]
                tree[i].id_name = id_name
            i += 1
        yield tree

def semev_output(lang, tree, annotated_funs):
    lemmas = [t.lemma for t in tree]
    funs   = [{l.name().lower(): l.key() for l in wn.synset(f).lemmas(lang=lang)}
              if f else None for f in annotated_funs]
    res    = [funs[i][lemmas[i]] if funs[i] and lemmas[i] in funs[i] else None
              for i in range(len(funs))]
    ids    = [t.id_name if 'id_name' in dir(t) else None for t in tree]

    for fun, name in zip(res, ids):
        if fun and name:
            print('\t'.join([name, name, 'wn:' + fun]))
    
def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--lang',
        choices=['en', 'it', 'es'],
        default='en'
    )
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
    parser.add_argument('--skip-long',
        action='store_true',
        help='dont try to evaluate sentences with more possibilities than num'
    )
    parser.add_argument('--model',
        choices=['unigram', 'interpolation', 'bigram'],
        default='interpolation'
    )
    parser.add_argument('--probs',
        nargs='?',
        default='../results/nodep_wn_autoparsed_th50.cnt'
    )
    parser.add_argument('--database',
        nargs='?',
        default='../probs.db'
    )
    parser.add_argument('--num', '-n',
        nargs='?',
        type=int,
        default=10000
    )
    return parser.parse_args()

SEMEV_DIR='../data/semeval2015/SemEval-2015-task-13-v1.0/data/'
PARSED_DIR='../data/semeval2015/'
LANG = {'en': 'eng', 'it': 'ita', 'es':'spa'}
if __name__ == '__main__':

    args = parse_args()

    if args.model == 'interpolation' and args.deprel:
        args.model = models.InterpolationDeprel
    elif args.model == 'interpolation':
        args.model = models.Interpolation
    elif args.model == 'bigram' and args.deprel:
        args.model = models.BigramDeprel
    elif args.model == 'bigram':
        args.model = models.Bigram
    elif args.model == 'unigram':
        args.model = models.Unigram

    parsed_file = PARSED_DIR + \
        'semeval_sentences_{}_udpipe_v2.conllu'.format(args.lang)
    semeval_file = SEMEV_DIR + \
        'semeval-2015-task-13-{}.xml'.format(args.lang)

    with open(parsed_file) as f:
        udpipe = list(udpipe_data(f))
        semeval = list(semeval_data(semeval_file))
        data = list(combine(semeval, udpipe))


        ev = evaluation.Evaluation(args)
        for tree in tqdm(data):
            funs = ev.annotate(tree, skip_long=args.skip_long, max_perm=args.num)
            if funs:
                semev_output(LANG[args.lang], tree, funs)
