import pgf
from typing import List
from ud_treebank_test import parse_connlu_file



def abstract_functions(cnc, graph):
    for id in graph.nodes:
        node = graph.get_by_address(id)
        if id != 0:
            funcs = [word for word, _, _ in cnc.lookupMorpho(node['word'].lower())]
            yield (funcs, node['head'])


def to_unigram(abstr_func_tuples):
    unigrams = []
    for t in abstr_func_tuples:
        funcs = t[0]
        if len(funcs) > 0:
            unigrams.append((funcs, 1.0))
    return unigrams


def to_bigram(abstr_func_tuples):
    tuple_list = list(abstr_func_tuples)
    bigrams = []
    for t in tuple_list:
        funcs = t[0]
        head_funcs = tuple_list[t[1] - 1]
        combinations = [(x,y) for x in funcs for y in head_funcs]
        bigrams.extend(combinations)
    return bigrams


UD_FILE = 'en-ud-dev.conllu'
if __name__ == "__main__":
    gr = pgf.readPGF('Dictionary.pgf')
    eng = gr.languages['DictionaryEng']
    graphs = parse_connlu_file(UD_FILE)
    g = graphs.__next__()
    print(to_bigram(abstract_functions(eng, g)))