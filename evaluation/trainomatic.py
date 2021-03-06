import xml.etree.ElementTree as ET
import os
from itertools import chain
from utils import UDNode
try:
    from tqdm import tqdm
except:
    tqdm = lambda x: x


# FUNCTIONS TO HANDLE UD PARSED TRAINOMATIC DATA

def trainomatic(data_file, sense_file):
    for sense_line in sense_file:
        wnid = int(sense_line.strip().split('\t')[0].split(':')[1])
        conllu = [] 
        while True:
            data_line = data_file.readline()
            if not data_line or data_line == '\n':
                break
            elif not data_line.startswith('#'): 
                conllu.append(data_line)
        ud_tree = [UDNode(l) for l in conllu]
        
        yield wnid, ud_tree

def trainomatic_sentences(sense_file):
    for sense_line in sense_file:
        wnid = int(sense_line.strip().split('\t')[0].split(':')[1])
        sent = sense_line.strip().split('\t')[1]
        
        yield wnid, sent


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
