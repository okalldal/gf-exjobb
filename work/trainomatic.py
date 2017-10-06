import xml.etree.ElementTree as ET
import os
from itertools import chain
from tqdm import tqdm

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