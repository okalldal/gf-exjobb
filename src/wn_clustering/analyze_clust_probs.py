#cat $2 | python analyze_clust_probs.py $1 bigram_obj.cnt noun_cond_obj.cnt verb_cond_obj.cnt > new_cnt.cnt
import sys
from nltk.corpus import wordnet as wn
from signal import signal, SIGPIPE, SIG_DFL
import argparse

delimiter= '\t'

signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser()
parser.add_argument('dict', type=argparse.FileType('r'))
parser.add_argument('bigramcnt', type=argparse.FileType('r'))
parser.add_argument('nouncond', type=argparse.FileType('r'))
parser.add_argument('verbcond', type=argparse.FileType('r'))
args = parser.parse_args()

full2clust=dict()
for line in args.dict:
    l_split=line.strip('\n').split(delimiter)
    full2clust[l_split[0]]=l_split[1]
bigram_probs=dict()
for line in args.bigramcnt:
    l_split=line.strip('\n').split(delimiter)
    bigram_probs[(l_split[1],l_split[2])]=float(l_split[0])
noun_probs=dict()
for line in args.nouncond:
    l_split=line.strip('\n').split(delimiter)
    clust_noun=l_split[0]
    i=1
    #print(clust_noun,l_split[1:],file = sys.stderr)
    while i<len(l_split):
        noun_probs[(l_split[i],clust_noun)]=float(l_split[i+1])
        i=i+2
verb_probs=dict()
for line in args.verbcond:
    l_split=line.strip('\n').split(delimiter)
    clust_verb=l_split[0]
    i=1
    while i<len(l_split):
        verb_probs[(l_split[i],clust_verb)]=float(l_split[i+1])
        i=i+2
for line in sys.stdin:
    l_split=line.strip('\n').split(delimiter)
    count=float(l_split[0])
    noun=l_split[1]
    verb=l_split[2]
    if noun in full2clust.keys() and verb in full2clust.keys(): 
        clustnoun=full2clust[noun]
        clustverb=full2clust[verb]
        clustprob=bigram_probs[(clustnoun,clustverb)]*noun_probs[(noun,clustnoun)]*verb_probs[(verb,clustverb)]
        print(count,clustprob,noun,verb,sep=delimiter)

