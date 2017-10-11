from nltk.corpus import wordnet as wn
from collections import Counter, defaultdict
from tqdm import tqdm
import pycountry

wn.langs()
noun_sss = wn.all_synsets('n')
no_synsets = 0

print('total')
langs = wn.langs()
counters = defaultdict(Counter)

for synset in tqdm(noun_sss, total=82115):
    no_synsets = no_synsets + 1
    for lang in wn.langs():
        counters[lang].update([len(synset.lemmas(lang))])
        if len(synset.lemmas(lang)) == 61:
            print(synset)
for lang in wn.langs():
    print(lang, counters[lang])
