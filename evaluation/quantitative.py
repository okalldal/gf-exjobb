import trainomatic
import spacy
from collections import defaultdict
from itertools import product, groupby
from utils import read_probs, read_poss_dict, Word
from numpy import log
import logging 
# import pgf
from nltk.corpus import wordnet as wn
import argparse

# TODO fix Pron
def get_bigrams_for_lemmas(lemmas, sentence, parser):
    bigrams = [(w,h) for w, h in get_bigrams(sentence, parser) 
               if w.lemma in lemmas or h.lemma in lemmas]
    return list(set(bigrams))


def get_bigrams(sentence, parser):
    tree = parser(sentence)
    return [(Word(w.lemma_, w.pos_), Word(w.head.lemma_, w.head.pos_) if w.dep_ != 'ROOT' else Word('ROOT')) 
            for w in tree]


def possible_bigrams(bigrams, possdict):
    vocab = set()
    vocab.update(w for w, _ in bigrams if not w.is_root and possdict[w])
    vocab.update(h for _, h in bigrams if not h.is_root and possdict[h])
    reduced_dict = [[(w, poss) for poss in possdict[w]] for w in vocab]
    permutations = product(*reduced_dict)
    for replacements in permutations:
        swapdict = dict(replacements) # swap word for abstract function
        swap = lambda w: swapdict[w] if w in vocab else w.lemma # Don't swap 'ROOT' etc
        yield [(swap(w), swap(h)) for w, h in bigrams]


# TODO make this nicer
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


def run(sentences, spacy_en, probs, possdict, linearize, wn2fun):
    lemma_not_found = 0
    prob_not_found = 0
    success = 0
    total = 0
    ambig = 0
    ambig_total = 0

    for i, (wnid, sentence) in enumerate(sentences):
        total += 1

        fun = wn2fun[wnid] 
        if not fun:
            continue
        lemmas = linearize(fun) 
        bigrams = get_bigrams_for_lemmas(lemmas, sentence, spacy_en)

        if not bigrams:
            lemma_not_found += 1
            continue

        rank = [(bigrams_prob(b, probs), b) 
                for b in possible_bigrams(bigrams, possdict)]
        is_ambig = len(rank) > 1
        rank = sorted(rank, key=lambda x: x[0])
       
        if is_ambig:
            ambig_total += 1 
        
        """ FIRST """
        p, first = rank[0]
        in_top = any(w == fun or h == fun for (w, h) in first)
                
        """ ORACLE
        p, top = next(groupby(rank, lambda x: x[0]))
        in_top = any(any(w == fun or h == fun for w, h in b) for p, b in top)
        """

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
    logging.info('Loading Spacy')
    spacy_en = spacy.load('en_depent_web_md')
    logging.info('Loading Probabilities')
    probs = defaultdict(lambda: 0, read_probs(args.probs))
    possdict = read_poss_dict(path=args.possdict)
    if args.dict == 'gf':
        """ GF """
        logging.info('Loading GF')
        lgr  = pgf.readPGF('../data/translate-pgfs/TranslateEng.pgf').languages['TranslateEng']
        wn2fun = defaultdict(lambda: None, read_wnid2fun('../data/Dictionary.gf'))
        linearize = lambda x: [lgr.linearize(pgf.ReadExpr(x))]
    elif args.dict == 'wn':
        """ Wordnet """
        logging.info('Loading Wordnet')
        wn2fun = defaultdict(lambda: None, {s.offset(): s.name() for s in wn.all_synsets()})
        linearize = lambda x: wn.synset(x).lemma_names()
    logging.info('Initialization finished')

    return spacy_en, probs, possdict, linearize, wn2fun


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--possdict', 
        nargs='?',
        default='../data/possibility_dictionaries/wn/eng.txt'
    )
    parser.add_argument('--dict', '-d'
        choices=['wn', 'gf']
    )
    parser.add_argument('--probs',
        nargs='?'
        default='../results/'
    )
    args = parser.parse_args()
        
    res = subprocess.run(['awk', '{a=a+$1}END{print a}', 'gf_autoparsed_th50.cnt'],
            stdout=subprocess.PIPE)
    total = float(res.stdout.decode().strip())

    sentences = wordnet_examples(pos_filter='n')
    run(sentences, *init(args))
