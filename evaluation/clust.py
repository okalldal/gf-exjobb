from collections import defaultdict
import models

PATH = '../data/possibility_dictionaries/wn_clust.tsv'
def read_mapping(filepath):
        with open(filepath) as f:
            ls = (l.strip().split('\t') for l in f)
            return defaultdict(lambda: None, ls)

wn2clust = read_mapping(PATH)
clust2wn = dict()
for synset, cluster in wn2clust.items():
    if cluster in clust2wn:
        clust2wn[cluster].append(synset)
    else:
        clust2wn[cluster] = [synset]

unigram = models.Unigram('../probs.db', 'nodep_wn_autoparsed_th50_uni')

class Cluster():
    def __init__(self, synset):
        self.cluster = wn2clust[synset]

    def top_synset(self, lemma=None):
        synsets = self.synsets(lemma)
        top = sorted([(unigram.get(s), s) for s in synsets], 
                key=lambda x: x[0], reverse=True)
        return next(top)[1]

    def synsets(self, lemma=None):
        """return possible synsets matching this lemma"""
        synsets = clust2wn[self.cluster]
        if not lemma:
            return synsets
        ls = lambda s: [s.lower() for l in wn.synset(s).lemma_names()]
        return [s for s in synsets if lemma in ls(s)]


    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.cluster
        else:
            return other == self
