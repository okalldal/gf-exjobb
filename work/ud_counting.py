import pgf
import pickle
from ud_treebank_test import parse_connlu_file
from collections import Counter
import itertools

def abstract_functions(cnc, graph):
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
    def funs(string):
        if string is None: return []
        return frozenset(
            [word for (word,_,_) in cnc.lookupMorpho(string.lower())]
        )

    def funs_dict(node):
        return dict(funs=funs(node['word']), head=node['head'])

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
            if len(combinations) > 0: 
                bigrams.append(frozenset(combinations))
    return bigrams


def create_data_for_fun(parse_fun, gf_lang, ud_path, out_path):
    graphs = parse_connlu_file(ud_path)
    parse_graphs = (parse_fun(abstract_functions(gf_lang, g)) for g in graphs)
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
        create_unigram_data(gf_lang, ud_path, out_path)
        print('wrote to file {}'.format(out_path))

        print('')
        print('creating bigram data')
        out_path = "{}-bigram-count.data".format(short)
        print('reading file {}'.format(ud_path))
        create_bigram_data(gf_lang, ud_path, out_path)
        print('wrote to file {}'.format(out_path))


