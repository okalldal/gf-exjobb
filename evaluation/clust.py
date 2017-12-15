from collections import defaultdict
import models
from nltk.corpus import wordnet as wn

PATH = '../data/possibility_dictionaries/'
def read_mapping(filepath):
        with open(filepath) as f:
            ls = (l.strip().split('\t') for l in f)
            return defaultdict(lambda: None, ls)

wn2clust = None
clust2wn = None
def init_dicts(name):
    filepath = PATH + name + '.tsv'
    global wn2clust
    global clust2wn
    wn2clust = read_mapping(filepath)
    clust2wn = dict()
    for synset, cluster in wn2clust.items():
        if cluster in clust2wn:
            clust2wn[cluster].append(synset)
        else:
            clust2wn[cluster] = [synset]


unigram = models.Unigram('../probs.db', 'nodep_wn_autoparsed_th50_uni')

class Cluster():
    def __init__(self, synset):
        self.synset = synset
        self.cluster = wn2clust[synset]

    def top_synset(self, lemma=None):
        if not self.cluster:
            return self.synset

        synsets = self.synsets(lemma)
        if not synsets:
            return self.synset

        top = sorted([(unigram.get(s), s) for s in synsets], 
                key=lambda x: x[0], reverse=True)
        return top[0][1]

    def synsets(self, lemma=None):
        """return possible synsets matching this lemma"""
        if not self.cluster:
            return [self.synset]
        synsets = clust2wn[self.cluster]
        if not lemma:
            return synsets
        ls = lambda s: [l.lower() for l in wn.synset(s).lemma_names()]
        return [s for s in synsets if lemma in ls(s)]


    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.cluster
        else:
            return other.__repr__() == self.__repr__()

    def __repr__(self):
        return "Cluster('{}')".format(self.cluster)

    def __hash__(self):
        return hash(self.__repr__())
