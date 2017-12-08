from utils import UDNode

def tree_data(data_file):
    ud_tree = []
    while True:
        data_line = data_file.readline()
        if not data_line or data_line == '\n':
            break
        elif not data_line.startswith('#'):
            ud_tree.append(UDNode(data_line))
    yield ud_tree

with open('../data/semeval2015/semeval_sentences_en_udpipe.conllu') as f:
    tree = next(tree_data(f))

