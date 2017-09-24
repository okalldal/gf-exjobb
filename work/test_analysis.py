import parse
import analysis
from itertools import chain

def matching_probs(node):
    lemma = node.lemma
    c = node.upostag
    cats = parse.POSSIBLE_GF_CATS_BY_UD_CAT[c]
    pattern = re.compile("%s.*(%s)" % (lemma, "|".join(cats)))
    matches = [f for f, p in probs if pattern.match(f)]
    if len(matches) == 0: 
        return ['OOV_' + c]
    else:
        return matches


def bigram_tuples(graph, gf_funs):
    childs = lambda h: [(n, h) for n in graph if n.head == h.id]
    pairs = chain.from_iterable(childs(n) for n in g)
    return [(gf_funs[a.id], gf_funs[b.id]) for a,b in pairs]

    
if __name__ == '__main__':
    bigram_probs = analysis.read_probs('../results/bigram_Eng.probs')
    unigram_probs = analysis.read_probs('../results/unigram_Eng.probs')

    gs = parse.parse_conllu_file("../data/UD_English/en-ud-dev.conllu")
    g = next(gs)
    gf_funs = ['from_Prep', 'OOV_DET', 'OOV_NOUN', 'come_V', 'this_Quant', 'story_N', 'OOV_PUNCT']

    tuples = bigram_tuples(g, gf_funs)
    tree_prob = analysis.calculate_tree_probability(tuples, bigram_probs, unigram_probs)
    print(tree_prob)

