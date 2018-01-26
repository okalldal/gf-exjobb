from sys import stdin,stdout
from struct import pack
word2id=dict()
i = 0
with open('vocab.txt') as v:
    for l in v:
        i=i+1
        word2id[l.split()[0]]=i
for l in stdin:
    l_split=l.strip('\n').split('\t')
    if l_split[2] in ['NOUN', 'VERB', 'ADJ', 'ADV']:
        dep = l_split[1]+"_"+l_split[2]
    else:
        dep = l_split[2]
    if dep not in word2id.keys():
        continue
    if l_split[3] == 'root':
        head='ROOT'
    elif l_split[5] in ['NOUN', 'VERB', 'ADJ', 'ADV']:
        head = l_split[4]+"_"+l_split[5]
    else:
        head = l_split[5]
    if head not in word2id.keys():
        continue
    dep = word2id[dep]
    head = word2id[head]
    stdout.buffer.write(pack('iid',dep,head,float(l_split[0])))
