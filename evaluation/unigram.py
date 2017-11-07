from nltk.corpus import wordnet as wn
from utils import read_poss_dict, Word
from evaluation import wordnet_examples
from itertools import chain
from collections import defaultdict

POS = {'n': 'NOUN', 'a': 'ADJ', 'v': 'VERB', 'r': 'ADV'}

def read_probs(filepath):
    with open(filepath) as f:
        lines = (l.strip().split('\t') for l in f)
        d = defaultdict(lambda: 0, {l[0]: float(l[1]) for l in lines})
    return d


if __name__ == '__main__':
    sentences = wordnet_examples()
    wndict = {s.offset(): s for s in wn.all_synsets()}
    possdict = read_poss_dict('../data/possibility_dictionaries/wn/eng.txt')
    probdict = read_probs('../results/wn_unigram_probs_autoparsed.probs')
    print('loading finished')
    total = 0
    success = 0
    for wnid, sentence in sentences:
        fun = wndict[wnid]
        if fun.pos() not in POS:
            continue
        lemmas = [Word(l, POS[fun.pos()]) for l in fun.lemma_names()]
        probs = (((probdict[poss], poss) for poss in possdict[l]) for l in lemmas)
        rerank = sorted(chain(*probs), key=lambda x: x[0], reverse=True)
        p, top = rerank[0]
        if p > 0:
            total += 1
        if p > 0 and top == fun.name():
            success += 1
        
    print('Success: {}/{}'.format(success, total))