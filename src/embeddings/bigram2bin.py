from sys import stdin,stdout
from struct import pack
word2id=dict()
i = 0
with open('vocab') as v:
    for l in v:
        i=i+1
        word2id[l.split()[0]]=i
for l in stdin:
    l_split=l.strip('\n').split()
    stdout.buffer.write(pack('iid',word2id[l_split[1]],word2id[l_split[2]],float(l_split[0])))
