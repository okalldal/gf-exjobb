from trainomatic import trainomatic
from collections import defaultdict
from itertools import product, groupby, islice
from functools import reduce
from operator import mul
from utils import read_probs, read_poss_dict, Word, reverse_poss_dict
from math import log
import logging 
import sys
import random
from nltk.corpus import wordnet as wn
from argparse import ArgumentParser
from os.path import basename, splitext
import models
from tqdm import tqdm


class EvaluationError():
    def __init__(self, error_type):
        self.error_type = error_type

class Evaluation():
    def __init__(self, **args):
        logging.info('Inititialization')

        self.tablename = splitext(basename(args.probs))[0]
        self.use_deprel = args.deprel
        if not args.model and self.use_deprel:
            self.model = models.InterpolationDeprel(args.database, self.tablename)
        elif not model:
            self.model = models.Interpolation(args.database, self.tablename)
        else:
            self.model = model(args.database, self.tablename)
        self.possdict = read_poss_dict(path=args.possdict)
        self.linearize = reverse_poss_dict(args.possdict)
        logging.info('Initialization:Finished')

    def abstract_funs_size(self, tree):
        """How many abstract function combinations"""
        vocab = set((w.lemma, w.upostag) for w in tree if w)
        vocab_possibilities = [[(w, poss) for poss in self.possdict[w]] 
                for w in vocab if self.possdict[w]]
        n_comb = reduce(mul, (len(s) for s in vocab_possibilities), 1)
        return n_comb

    def abstract_funs_gen(self, tree, max_perm=float('inf'), skip_long=False):
        """Returning an iterator with possible abstr funs for tree"""
        vocab = set((w.lemma, w.upostag) for w in tree if w)

        n_comb = self.abstract_funs_size(tree)
        if skip_long and n_comb > max_perm:
            return None

        vocab_possibilities = [[(w, poss) for poss in self.possdict[w]] 
                for w in vocab if self.possdict[w]]
        permutations = product(*vocab_possibilities)
        for i, replacements in enumerate(permutations):
            if i >= max_perm:
                break
            # swap word for abstract function
            swap = defaultdict(lambda: None, replacements)
            yield [swap[(node.lemma, node.upostag)] if node else None for node in tree]

    def to_bigrams(self, abstract_funs, tree):
        """ take a ADT and a UD tree and return abstract bigrams"""
        return [(abstract_funs[i], abstract_funs[node.head], node.deprel)
            for i, node in enumerate(tree)]

    def to_pos(self, tree):
        """ takes a UD tree and return POS bigrams"""
        return [(node.upostag.upper(), tree[node.head].upostag.upper(),
            node.deprel)
            for i, node in enumerate(tree)]

    def rank(self, trees):
        """take a ADT iterator and returns the top"""
        for abstract_funs in trees:
            bigrams = self.to_bigrams(abstract_funs, tree)
            pos = self.to_pos(tree)
            
            try:
                p = 0
                for bs, pos in zip(bigrams, pos):
                    p += -log(self.model.get(bs, pos))
            except ValueError:
                # No probability found
                logging.warn('No probability found for funs %s' % abstract_funs)
                continue

            if not best or p < p_best:
                p_best = p
                best = abstract_funs

        return best

    def annotate(self, tree, max_perm=10000, progress_bar=False):
        """take a UD tree and return the top ADT"""
        best = None 
        p_best = None
        n_combs = self.abstract_funs_size(tree)
        funs = self.abstract_funs_gen(tree, max_perm=max_perm)
        if not funs:
            return None

        if progress_bar:
            funs = tqdm(funs, total=min(max_perm, n_combs))

        return self.rank(funs)

    def filter_for_node(self, node, tree):
        heads_for_node = [tree[n.head] for n in tree if n == node]
        filtered_tree = [
            n if n == node or             # nodes with lemma
                 tree[n.head] == node or  # nodes with lemma as head
                 n in heads_for_node      # nodes that are head
            else None
            for n in tree
        ]
        return filtered_tree

