from collections import Counter, Iterable
import pgf

def write_function_list(grammar, out_path):
    '''
    Writes a file with all GF abstract functions.
    :param grammar: pgf.PGF
    :param out_path: str
    :return:
    '''

    funs_tuples = []
    # Generate tuples with functions names and category
    funs = ((fun, cat) for cat in grammar.categories
                       for fun in grammar.functionsByCat(cat))
    
    with open(out_path, 'w+') as f:
        for fun, cat in funs_tuples:
            f.write('{}\t{}\n'.format(fun, cat))


def read_function_list(path):
    """
    Read the GF abstract functions file
    :param path:
    :return:
    """
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


#CONLLU_FIELD_NAMES = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']


class UDNode:
    def __init__(self, conllu_node_line):
        field_values = conllu_node_line.split('\t')
        self.id = int(field_values[0]) - 1
        self.form = field_values[1]
        self.lemma = field_values[2]
        self.upostag = field_values[3]
        self.xpostag = field_values[4]
        self.feats = field_values[5].split('|')
        self.head = int(field_values[6]) - 1
        self.deprel = field_values[7]
        self.deps = field_values[8]
        self.misc = field_values[9]

    def __str__(self):
        return 'UDNode ' + self.form + ' (' + str(self.head) + ')'

    def __repr__(self):
        return self.__str__()


def parse_conllu_file(file_path: str):
    '''
    Reads a conllu_file and gives an iterator of all graphs in the file, each graph is
    given as a list of its nodes sorted by id.
    :param file_path:
    :return:
    '''
    with open(file_path, encoding='utf-8') as f:
        current = []
        for line in f:
            if line == "\n":
                yield [UDNode(node_line) for node_line in current]
                current = []
            elif not line.startswith('#'):
                current.append(line)


def generate_bigrams(graph):
    '''
    Generates all (dependent, head) pairs in a graph, if dependent is already the root word
    head is None
    :param graph:
    :return:
    '''
    for node in graph:
        head = graph[node.head] if node.head != -1 else None
        yield node, head


def lookupmorpho_possible_functions(node, gf_language, oov_fallback=True):
    '''
    Gives all possible GF-functions for a node given its FORM and a given concrete grammar.
    :param node:
    :param gf_language:
    :param oov_fallback:
    :return:
    '''
    possible_functions = [gf_function for gf_function, _, _ in gf_language.lookupMorpho(node.form.lower())]
    if len(possible_functions)==0 and oov_fallback:
        possible_functions = ['OOV_' + node.upostag]
    return possible_functions


def lookupmorpho_unigram_feature_generator(graph, gf_language, use_deprel=False):
    for node in graph:
        if use_deprel:
            yield frozenset((fun, node.deprel) for fun in lookupmorpho_possible_functions(node, gf_language))
        else:
            yield frozenset(lookupmorpho_possible_functions(node, gf_language))


def lookupmorpho_bigram_feature_generator(graph, gf_language, use_deprel=False):
    for node, head in generate_bigrams(graph):
        node_possible_functions = lookupmorpho_possible_functions(node, gf_language)
        head_possible_functions = lookupmorpho_possible_functions(head, gf_language) if head else ['ROOT']
        if use_deprel:
            combinations = [(x, y, node.deprel) for x in node_possible_functions for y in head_possible_functions]
        else:
            combinations = [(x, y) for x in node_possible_functions for y in head_possible_functions]
        yield frozenset(combinations)


def test_unigram_feature_generator(graph):
    for node in graph:
        yield node.lemma


def test_bigram_feature_generator(graph):
    for node, head in generate_bigrams(graph):
        node_lemma = node.lemma
        head_lemma = head.lemma if head else "ROOT"
        yield node_lemma, head_lemma

def count_features(graphs, *graph2occurences):
    '''
    This function takes an iterable of UD-graphs and a set of occurrence generators. An occurrence generator is a
    function accepting one graph and returning a list of occurrences for this graph. One occurrence typically consist of
    a set of features describing one node in the graph so that each node in the graph will result in one
    occurrence. The feature sets making up each occurrence must be hashable. For each occurrence generator this method
    will return a Counter giving the total counts over all graphs for each unique feature set given by
    that occurrence generator.
    :param graphs:
    :param graph2features: a function taking a graph and returning a list of hashable objects
    :return:
    '''
    counters = [Counter() for _ in graph2occurences]
    for graph in graphs:
        for counter, graph2occurence in zip(counters, graph2occurences):
            counter.update(graph2occurence(graph))
    return counters if len(counters) > 1 else counters[0]
