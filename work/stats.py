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
    for tuple in abstr_func_tuples:
        funcs = tuple[0]
        if len(funcs) > 0: yield (funcs, 1.0)


def to_bigram(abstr_func_tuples):
    tuple_list = list(abstr_func_tuples)
    for tuple in tuple_list:
        funcs = tuple[0]
        head_funcs = tuple_list[tuple[1] - 1]



UD_FILE = 'en-ud-dev.conllu'
if __name__ == "__main__":
    gr = pgf.readPGF('Dictionary.pgf')
    eng = gr.languages['DictionaryEng']
    graphs = parse_connlu_file(UD_FILE)
    g = graphs.__next__()