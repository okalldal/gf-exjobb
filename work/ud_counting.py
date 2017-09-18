import pgf
import pickle
from ud_treebank_test import parse_connlu_file
from collections import Counter
import itertools

GF2UD_CATS = {
    "N": "NOUN",
    "N": "PROPN",
    "PN": "PROPN",
    "A": "ADJ",
    "V": "VERB",
    "V2": "VERB",
    "V3": "VERB",
    "VV": "VERB",
    "VA": "VERB",
    "VV": "AUX",
    "VS": "VERB",
    "VQ": "VERB",
    "V2V": "VERB",
    "V2A": "VERB",
    "V2S": "VERB",
    "V2Q": "VERB",
    "VP": "VERB",
    "AdA": "ADV",
    "AdN": "ADV",
    "AdV": "ADV",
    "Adv": "ADV",
    "CAdv": "ADV",
    "IAdv": "ADV"
}

def check_compatibility_categories(ud_category, gf_category):
    return GF2UD_CATS[gf_category] != ud_category

def abstract_functions(gr, cnc, graph, only_matching_ud_gf_cats=False, ud_categories=None, gf_categories=None):
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

    def get_gf_functions(word, ud_category):
        if word is None: return [], []

        gf_functions = set()
        unfiltered_gf_functions = set()
        for gf_function, _ , _ in cnc.lookupMorpho(word.lower()):
            gf_category = gr.functionType(gf_function).cat

            # perform filtering to get only matching categories
            if only_matching_ud_gf_cats and check_compatibility_categories(ud_category, gf_category):
                pass
            elif gf_categories is not None and gf_category not in gf_categories:
                unfiltered_gf_functions.add(gf_function)
            else:
                unfiltered_gf_functions.add(gf_function)
                gf_functions.add(gf_function)

        # check if ud_category is valid
        if ud_categories is not None and ud_category not in ud_categories:
            return [], frozenset(unfiltered_gf_functions)
        else:
            return frozenset(gf_functions), frozenset(unfiltered_gf_functions)

    def get_node_data(node):
        gf_functions_filtered, gf_functions_unfiltered = get_gf_functions(node['word'], node['ctag'])
        return dict(funs=gf_functions_filtered, all_funs=gf_functions_unfiltered, head=node['head'])

    return {address: get_node_data(node) for address, node in graph.nodes.items()}


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
    for address, data in abstr_func_dicts.items():
        if data['head'] is not None:
            node_functions = data['funs']
            head_functions = abstr_func_dicts[data['head']]['all_funs']
            # get all possible pairings of node and head functions
            combinations = [(x, y) for x in node_functions for y in head_functions]
            if len(combinations) > 0:
                bigrams.append(frozenset(combinations))
    return bigrams


def create_data_for_fun(parse_fun, gf_grammar, gf_lang, ud_path, out_path, ud_filter, gf_filter):
    graphs = parse_connlu_file(ud_path)
    parse_graphs = (
        parse_fun(abstract_functions(gf_grammar, gf_lang, g, ud_categories=ud_filter, gf_categories=gf_filter))
        for g in graphs)
    occurences = itertools.chain.from_iterable(parse_graphs)
    with open(out_path, 'w+') as f:
        for occ in occurences:
            f.write(str(list(occ)) + '\n')

def create_bigram_data(*args):
    create_data_for_fun(to_bigram, *args)


def create_unigram_data(*args):
    create_data_for_fun(to_unigram, *args)


if __name__ == "__main__":
    gr = pgf.readPGF('Dictionary.pgf')

    for lang, short in [('English', 'en')]: #[('English', 'en'), ('Swedish', 'sv'), ('Bulgarian', 'bg')]:
        print(lang)
        gf_lang = gr.languages['Dictionary' + lang[:3]]
        ud_path = "UD_{}/{}-ud-train.conllu".format(lang, short)
        out_path = "{}-unigram-count.data".format(short)
        print('creating unigram data')
        print('reading file {}'.format(ud_path))
        create_unigram_data(gr, gf_lang, ud_path, out_path, {"NOUN"}, {"N"})
        print('wrote to file {}'.format(out_path))

        print('')
        print('creating bigram data')
        out_path = "{}-bigram-count.data".format(short)
        print('reading file {}'.format(ud_path))
        create_bigram_data(gr, gf_lang, ud_path, out_path, {"NOUN"}, {"N"})
        print('wrote to file {}'.format(out_path))


