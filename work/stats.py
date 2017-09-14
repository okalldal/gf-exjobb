from ud_treebank_test import parse_connlu_file
from collections import Counter
import numpy as np
import itertools

GF2UD_CATS = {
    "N":       "NOUN",
    "N":      "PROPN",
    "PN":      "PROPN",
    "A":       "ADJ",
    "V":       "VERB",
    "V2":      "VERB",
    "V3":      "VERB",
    "VV":      "VERB",
    "VA":      "VERB",
    "VV":      "AUX",
    "VS":     "VERB",
    "VQ":      "VERB",
    "V2V":     "VERB",
    "V2A":     "VERB",
    "V2S":     "VERB",
    "V2Q":     "VERB",
    "VP":      "VERB",
    "AdA":     "ADV",
    "AdN":     "ADV",
    "AdV":     "ADV",
    "Adv":     "ADV",
    "CAdv":    "ADV",
    "IAdv":    "ADV"
}

def abstract_functions(gr, cnc, graph, filter_cats=True):
    """Traverses a graph and gives the abstract functions and the head for each node.
    
    Example output: 
    {
        0: {'funs': [], 'head': None},
        1: {'funs': ['tell_from_V3', 'peel_away_from_V2', 'from_Prep',], 'head': 3},
        2: {'funs': [], 'head': 3},
        3: {'funs': [], 'head': 4},
        4: {'funs': ['come_V', 'come_over_V'], 'head': 0},
        5: {'funs': ['this_Quant'], 'head': 6},
        6: {'funs': ['story_N'], 'head': 4},
        7: {'funs': [], 'head': 4}
    }
    """
    def funs(word, cat):
        if word is None: return []
        return frozenset(
            [fun for (fun,_,_) in cnc.lookupMorpho(word.lower()) if not filter_cats or GF2UD_CATS[gr.functionType(fun)] == cat]

        )

    def funs_dict(node):
        return dict(funs=funs(node['word'], node['ctag']), head=node['head'])

    return {address: funs_dict(node) for address, node in graph.nodes.items()}


def to_unigram(abstr_func_dicts):
    """Gives a list of unigram occurences"""
    unigrams = []
    for adr, d in abstr_func_dicts.items():
        funcs = d['funs']
        if len(funcs) > 0:
            unigrams.append(funcs)
    return unigrams


def to_bigram(abstr_func_dicts):
    bigrams = []
    for adr, d in abstr_func_dicts.items():
        if d['head'] is not None:
            funcs = d['funs']
            head_funcs = abstr_func_dicts[d['head']]['funs']
            combinations = [(x,y) for x in funcs for y in head_funcs]
            bigrams.append(frozenset(combinations))
    return bigrams


def convert_possibilities_to_ids(occurences):
    occurency_tuples = []
    possibility2id = dict()
    current_id = 0
    for occurency, count in dict(occurences).items():
        possibility_ids = []
        for possibility in occurency:
            if possibility not in possibility2id.keys():
                possibility2id[possibility] = current_id
                possibility_ids.append(current_id)
                current_id = current_id + 1
            else:
                possibility_ids.append(possibility2id[possibility])
        if len(possibility_ids) > 0:
            occurency_tuples.append((possibility_ids, count))
    return occurency_tuples, possibility2id


def em_algorithm(occurrence_tuples, init_probs, convergence_threshold):
    """occurrence_tuples : [([int],int)], init_probs : np.[double], convergence_threshold : double"""
    convergence_diff = convergence_threshold
    current_probs = init_probs
    total_counts = sum([count for _, count in occurrence_tuples])
    while convergence_diff >= convergence_threshold:
        new_probs = np.zeros(current_probs.shape)
        for possibilities, count in occurrence_tuples:
            possibility_probabilities = current_probs[possibilities]  # numpy advanced indexing
            total_probability = np.sum(possibility_probabilities)
            new_probs[possibilities] = new_probs[possibilities] + possibility_probabilities*count/total_probability
        prob_quotients = new_probs / current_probs
        threshold_mask = np.abs(prob_quotients) > 1e-50*total_counts    # used for numpy advanced indexing to remove differences
                                                                # caused by numerical imprecision
        convergence_diff = np.sum(new_probs[threshold_mask]*np.log(prob_quotients[threshold_mask]))/total_counts
        current_probs = new_probs
        print(convergence_diff)
    return current_probs/total_counts


UD_FILE = '../data/UD_English-r1.3/en-ud-train.conllu'

def run():
    gr = pgf.readPGF('Dictionary.pgf')
    eng = gr.languages['DictionaryEng']
    graphs = parse_connlu_file(UD_FILE)
    parse_graphs = (to_bigram(abstract_functions(gr,eng, g, filter_cats=False)) for g in graphs)
    occurences = Counter(itertools.chain.from_iterable(parse_graphs))
    del parse_graphs, graphs, gr, eng 
    occurency_tuples, occurency2id = convert_possibilities_to_ids(occurences)
    del occurences
    em_algorithm(occurency_tuples, np.ones([len(occurency2id)])/1e10, 1e-2)

if __name__ == "__main__":
    run()
