import xml.etree.ElementTree as ET
import os
from itertools import chain
try:
    from tqdm import tqdm
except:
    tqdm = lambda x: x
import bz2

# FUNCTIONS TO HANDLE UD PARSED TRAINOMATIC DATA

def trainomatic(data_file, sense_file):
    data = bz2.open(data_file)
    sense = open(sense_file)

    for sense_line in sense:
        wnid = int(sense_line.strip().split('\t')[0].split(':')[1])
        sent = sense_line.strip().split('\t')[1]
        conllu = [] 
        while True:
            data_line = data.readline().decode()
            if not data_line or data_line == '\n':
                break
            elif not data_line.startswith('#'): 
                conllu.append(data_line)
        ud_tree = [UDNode(l) for l in conllu]
        
        yield wnid, ud_tree

    data.close()
    sense.close()

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


# FUNCTIONS TO HANDLE RAW TRAINOMATIC DATA
DATA_DIR = '../data/TRAIN-O-MATIC-DATA/EN/EN.500-2.0'

def parse(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    assert(root.tag == 'corpus')
    assert[root[0].tag == 'lexelt']
    base = root[0].attrib['item']
    for instance in root[0]:
        wnid = instance[0].attrib['senseId'][3:-1]
        wnid = int(wnid)
        sentence = "".join(instance[1].itertext()).replace('.', ' . ')
        yield (wnid, sentence)

def parse_dir(dirpath = DATA_DIR, progress_bar=True):
    files = [os.path.join(dirpath, f) 
             for f in os.listdir(dirpath) if f.endswith('.xml')]
    if progress_bar: 
        files = tqdm(files)
    return chain.from_iterable(parse(f) for f in files)
