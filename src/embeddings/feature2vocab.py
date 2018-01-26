from sys import stdin
from collections import Counter
from nltk.corpus import wordnet as wn
root_count = 0
dep_counts = Counter()
wnlabels = {'NOUN':'n','VERB':'v','ADJ':'a','ADV':'r'}
lemmas=dict()
lemmas['NOUN']=set(wn.all_lemma_names('n'))
lemmas['VERB']=set(wn.all_lemma_names('v'))
lemmas['ADJ']=set(wn.all_lemma_names('a'))
lemmas['ADJ']=lemmas['ADJ']+set(wn.all_lemma_names('s'))
lemmas['ADV']=set(wn.all_lemma_names('r'))
for l in stdin:
    l_split = l.strip('\n').split('\t')
    if l_split[2] not in ['NOUN','VERB','ADJ','ADV']:
        continue
    if not l_split[1].islower():
        continue
    if l_split[1] not in lemmas[l_split[2]]:
        continue
    dep_counts[l_split[1]+"_"+l_split[2]]+=int(l_split[0])
    if l_split[3]=='root':
        root_count = root_count+int(l_split[0])

print('ROOT',root_count,sep=' ')
for item, count in dep_counts.most_common():
    print(item,count,sep=' ')
