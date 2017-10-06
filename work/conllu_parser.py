from collections import Counter
import logging


# Parse graps from a connlu file, a graph is a list of UDNode objects in order of UD id
def parse_conllu_file(file_path):
    '''
    Reads a conllu_file and gives an iterator of all graphs in the file, each graph is
    given as a list of its nodes sorted by id.
    :param file_path:
    :return:
    '''
    with open(file_path, encoding='utf-8') as f:
        current = []
        failed_parses = 0
        successful_parses = 0
        for line in f:
            if line == "\n":
                try:
                    yield parse_graph(current)
                    successful_parses = successful_parses + 1
                except Exception as ex:
                    logging.debug(ex)
                    failed_parses = failed_parses+1
                current = []
            elif not line.startswith('#'):
                current.append(line)
        logging.info('Parsed {} graphs successfully.'.format(successful_parses))
        if failed_parses > 0:
            logging.warning('Error with parsing {} of {} graphs.'.format(failed_parses, failed_parses+successful_parses))


def parse_graph(node_lines):
    return [UDNode(node_line) for node_line in node_lines]


# Count unique occurences of features
def count_features(graphs):
    counter = Counter()
    for graph in graphs:
        counter.update(bigram_features(graph))
    return counter


# Generate features for each node in graph
def bigram_features(graph):
    for node in graph:
        if node.head == -1:
            yield (node.lemma, node.form, node.upostag, node.deprel)
        else:
            head = graph[node.head]
            yield (node.lemma, node.form, node.upostag, node.deprel, head.lemma, head.form, head.upostag)


def print_feature_counts(feature_counts, path):
    with open(path, mode='w+', encoding='utf-8') as file:
        for feature, count in dict(feature_counts).items():
            print('\t'.join(list(feature)+[str(count)]), file=file)

def read_feature_counts(path):
    with open(path, mode='r', encoding='utf-8') as file:
        for l in file:
            l_split = l.split('\t')
            yield (tuple(l_split[:-1]), int(l_split[-1]))


#CONLLU_FIELD_NAMES = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
class UDNode:
    def __init__(self, conllu_node_line):
        field_values = conllu_node_line.split('\t')
        self.id = int(field_values[0]) - 1
        self.form = field_values[1]
        self.lemma = field_values[2]
        self.upostag = field_values[3]
        #self.xpostag = field_values[4]
        #self.feats = field_values[5].split('|')
        self.head = int(field_values[6]) - 1
        self.deprel = field_values[7]
        #self.deps = field_values[8]
        #self.misc = field_values[9]

    def __str__(self):
        return 'UDNode ' + self.form + ' (' + str(self.head) + ')'

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    conllu_files_train = {'Eng': '../data/UD_English/en-ud-train.conllu',
                          'Swe': '../data/UD_Swedish/sv-ud-train.conllu',
                          'Bul': '../data/UD_Bulgarian/bg-ud-train.conllu',
                          'Chi': '../data/UD_Chinese/zh-ud-train.conllu',
                          'Fin': '../data/UD_Finnish/fi-ud-train.conllu',
                          'Hin': '../data/UD_Hindi/hi-ud-train.conllu',
                          }
    for lang, conllu_file in conllu_files_train.items():
        graphs = parse_conllu_file(conllu_file)
        feature_counts = count_features(graphs)
        print_feature_counts(feature_counts, '../data/feature_counts/{}_train_features.txt'.format(lang))
