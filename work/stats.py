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
    id2possibility = []
    current_id = 0
    for occurency, count in dict(occurences).items():
        possibility_ids = []
        for possibility in occurency:
            if possibility not in possibility2id.keys():
                possibility2id[possibility] = current_id
                id2possibility.append(possibility)
                possibility_ids.append(current_id)
                current_id = current_id + 1
            else:
                possibility_ids.append(possibility2id[possibility])
        if len(possibility_ids) > 0:
            occurency_tuples.append((possibility_ids, count))
    return occurency_tuples, id2possibility


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
    return current_probs


def make_unigram_probabilities(all_functions_with_categories, function_counts, function2id):
    category_counts = dict()
    smoothed_counts = np.array(len(all_functions_with_categories))
    i = -1
    for function_name, category in all_functions_with_categories:
        i = i + 1
        if function_name in function2id.keys():
            smoothed_counts[i] = function_counts[function2id[function_name]] + 1
        else:
            smoothed_counts[i] = 1

        if category not in category_counts.keys():
            category_counts[category] = 1
        else:
            category_counts[category] = category_counts[category] + 1
    i = -1
    total_smoothed_count = np.sum(smoothed_counts)
    for function_name, _ in all_functions_with_categories:
        yield (function_name, smoothed_counts[i]/total_smoothed_count)
    for category, count in category_counts.items():
        yield (category, count)


def make_bigram_probabilities(bigram_counts, id2bigram):
    total_counts = np.sum(bigram_counts)
    for bigram, count in zip(id2bigram, list(bigram_counts)):
        yield (bigram, count/total_counts)


UD_FILE = '../data/UD_English-r1.3/en-ud-train.conllu'

from ast import literal_eval
def run():
    to_set = lambda x: frozenset(literal_eval(x.strip()))
    occurences = Counter(to_set(l) for l in open('en-unigram-count.data'))
    print('Finished reading file')
    occurency_tuples, id2possibility = convert_possibilities_to_ids(occurences)
    with open('ids.txt', 'w+') as f:
        for poss in id2possibility:
            f.write(str(poss) + '\n')
    print("Converted possibilities to id.")
    del occurences
    #id2possibility = dict(zip(possibility2id.values(), possibility2id.keys()))
    #possibilities = [id2possibility[i] for i in range(len(id2possibility))]
    #del possibility2id
    #del id2possibility
    #"Compiled possibility list"

    print(len(occurency_tuples))
    probabilities = em_algorithm(occurency_tuples, np.ones([len(id2possibility)])/1e10, 1e-5)
    print("Finished EM.")
    with open('probabilities.txt', 'w+') as f:
        for poss, prob in zip(id2possibility, probabilities):
            f.write(str(poss) + '\t' + str(prob) + '\n')
    print("Finished printing.")

if __name__ == "__main__":
    run()
