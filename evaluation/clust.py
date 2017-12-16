from collections import defaultdict
import models
from nltk.corpus import wordnet as wn

PATH = '../data/possibility_dictionaries/'
def read_mapping(filepath):
        with open(filepath) as f:
            ls = (l.strip().split('\t') for l in f)
            return defaultdict(lambda: None, ls)

class Cluster():

    def __init__(self, name):
        filepath = PATH + name + '.tsv'
        self.wn2clust = read_mapping(filepath)
        self.clust2wn = dict()
        for synset, cluster in wn2clust.items():
            if cluster in clust2wn:
                clust2wn[cluster].append(synset)
            else:
                clust2wn[cluster] = [synset]


    def cluster(self, synset):
        return wn2clust[synset] if synset in wn2clust.keys() else synset

    def synsets(self, synset, lemma=None):
        """return all synsets in same cluster matching this lemma"""
        if not self.cluster:
            return [self.synset]
        synsets = clust2wn[self.cluster]
        if not lemma:
            return synsets
        ls = lambda s: [l.lower() for l in wn.synset(s).lemma_names()]
        return [s for s in synsets if lemma in ls(s)]

