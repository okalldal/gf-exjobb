from nltk.corpus import wordnet as wn
from collections import Counter
import sys
counts = Counter()
tot_count=0
hyper=lambda s: s.hypernyms()
for line in sys.stdin:
    l_split=line.strip('\n').split('\t')
    count=float(l_split[0])
    tot_count=tot_count+count
    base_synset=wn.synset(l_split[1])
    counts[base_synset.name()]+=count
    for synset in base_synset.closure(hyper):
        counts[synset.name()]+=count
for synset, count in counts.most_common():
    print(count/tot_count,synset,sep='\t')

