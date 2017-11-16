from nltk.corpus import wordnet
import sys

wncat2udcat = {'n':'NOUN', 'v':'VERB', 'a':'ADJ', 's':'ADJ', 'r':'ADV'}

syns = list(wordnet.all_synsets())
offsets_list = [(s.offset(), s) for s in syns]
offsets_dict = dict(offsets_list)
delimiter='\t'
for l in sys.stdin:
    l_split = l.strip('\n').split(',')
    pl=l_split[1]
    wnid=int(l_split[3].split('-')[0])
    if wnid in offsets_dict.keys():
        ss = offsets_dict[wnid]
        print(pl, ss.name(), wncat2udcat[ss.pos()], sep=delimiter)
    else:
        print(pl, wnid, sep=delimiter, file=sys.stderr)
