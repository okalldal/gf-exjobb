import logging
import argparse
import sys
from signal import signal, SIGPIPE, SIG_DFL


# Parse graps from a connlu file, a graph is a list of UDNode objects in order of UD id
def parse_conllu_file(f):
    '''
    Reads a conllu_file and gives an iterator of all graphs in the file, each graph is
    given as a list of its nodes sorted by id.
    :param file_path:
    :return:
    '''
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


# Generate features for each node in graph
def bigram_features(graph):
    for node in graph:
        if node.head == -1:
            yield [node.lemma, node.form, node.upostag, node.deprel, 'root', 'root', 'root']
        else:
            head = graph[node.head]
            yield [node.lemma, node.form, node.upostag, node.deprel, head.lemma, head.form, head.upostag]


#CONLLU_FIELD_NAMES = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
class UDNode:
    def __init__(self, conllu_node_line):
        field_values = conllu_node_line.lower().split('\t')
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
    # ignore SIG_PIPE and don't throw exceptions on it
    signal(SIGPIPE, SIG_DFL)

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType(mode='r', encoding='utf-8'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType(mode='w', encoding='utf-8'), default=sys.stdout)
    args = parser.parse_args()
    graphs = parse_conllu_file(args.infile)
    for g in graphs:
        for feat in bigram_features(g):
            print('\t'.join(feat), file=args.outfile)
