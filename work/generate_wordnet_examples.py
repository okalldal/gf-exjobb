import pgf
from nltk.corpus import wordnet as wn

def read_funs2wordnetid(path):
    with open(path, encoding='utf-8') as f:
        for l in f:
            l_split = l.split()
            if len(l_split)==0 or l_split[0]!= 'fun':
                continue
            fun = l_split[1]
            l_splitbar = l.split('--')
            if len(l_splitbar)<2:
                continue
            try:
                wnid = int(l_splitbar[1].split()[0])
                yield fun, wnid
            except ValueError:
                continue

if __name__ == '__main__':
    import nltk
    with open('../results/example_sentences_wordnet.txt', mode='w+') as f:
        for fun, wnid in read_funs2wordnetid('../data/Dictionary.gf'):
            if wnid == 0:
                continue
            synset = wsd[wnid]
            if len(synset.examples()) == 0:
                continue
            print('#  fun: {}, wnid: {}'.format(fun, wnid), file=f)
            for example in synset.examples():
                print(example, file=f)