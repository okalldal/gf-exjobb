import itertools
import nltk

def parse_ud_file(file_path, out_path):
    """Converts .conllu file to our data format using PGF

    
    Requires GF bindings to be installed
    """
    # todo implement JSON
    pass


def parse_data(file_path):
    """Parses our data format.

    Do not require GF bindings.
    """
    # todo implement JSON
    pass


def write_function_list(grammar, out_path):
    """Writes a file with all GF abstract functions."""

    funs_tuples = []
    # Generate tuples with functions names and category
    funs = ((fun, cat) for cat in grammar.categories
                       for fun in grammar.functionsByCat(cat))
    
    with open(out_path, 'w+') as f:
        for fun, cat in funs_tuples:
            f.write('{}\t{}\n'.format(fun, cat))


def read_function_list(path):
    """Read the GF abstract functions file"""
    for line in open(path, encoding='utf8'):
        fun, cat = line.strip().split('\t')
        yield (fun, cat)


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


def abstract_functions(gr, cnc, graph, ud_categories=None, gf_categories=None, use_OOV_fallback = True):
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
        possible_functions = cnc.lookupMorpho(word.lower())
        if len(possible_functions) == 0 and use_OOV_fallback: return [], ['OOV_'+ud_category]
        for gf_function, _ , _ in possible_functions:
            gf_category = gr.functionType(gf_function).cat


            # perform filtering to get only matching categories
            if gf_categories is not None and gf_category not in gf_categories:
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


def parse_connlu_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        current = []
        for line in f:
            if line == "\n":
                connlu_string = ''.join(current)
                try:
                    yield nltk.parse.DependencyGraph(
                    tree_str=connlu_string, top_relation_label='root')
                except Exception as ex:
                    print('Error in parsing tree')
                    #print(connlu_string)
                current = []
            elif not line.startswith('#'):
                current.append(line)


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


import argparse
import sys
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse UD files using GF")
    parser.add_argument('file', 
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help="the UD '.conllu' file to use for parsing")
    parser.add_argument('-o', '--output', metavar="FILENAME",
                        type=argparse.FileType('w', encoding='UTF-8'), 
                        default=sys.stdout,
                        help='Where to save the parsed UD trees')
    #args = parser.parse_args()

    import pgf

    gr = pgf.readPGF('Dictionary.pgf')

    for lang, short in [('English', 'en'), ('Swedish', 'sv'), ('Bulgarian', 'bg')]:
        print(lang)
        gf_lang = gr.languages['Dictionary' + lang[:3]]
        ud_path = "UD_{}/{}-ud-train.conllu".format(lang, short)
        out_path = "{}-unigram-nouns.data".format(short)
        print('creating unigram data')
        print('reading file {}'.format(ud_path))
        create_unigram_data(gr, gf_lang, ud_path, out_path, {"NOUN"}, {"N"})
        print('wrote to file {}'.format(out_path))

        print('')
        print('creating bigram data')
        out_path = "{}-bigram-nouns.data".format(short)
        print('reading file {}'.format(ud_path))
        create_bigram_data(gr, gf_lang, ud_path, out_path, {"NOUN"}, {"N"})
        print('wrote to file {}'.format(out_path))

