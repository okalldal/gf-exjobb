from nltk.corpus import wordnet as wn
from tqdm import tqdm
cat_len = {'n':82115, 'v':13767, 'a':18156, 's':18156, 'r':3621}
def generate_possibility_dictionary(languages):
    from collections import defaultdict
    lang2lemma2fun = defaultdict(lambda: defaultdict(lambda: []))
    funs = []
    for cat in ['n', 'v', 'a', 's', 'r']:
        for synset in tqdm(wn.all_synsets(cat),total=cat_len[cat]):
            funs.append(synset.name())
            for lang in languages:
                lemmas = synset.lemma_names(lang.lower())
                lemmas.sort()
                for lemma in lemmas:
                    lang2lemma2fun[lang][lemma].append(synset.name())
    return lang2lemma2fun, funs

def write_possibility_dictionary(lang2cat2lemma2fun):
    for lang in wn.langs():
        for cat in ['n', 'v', 'a', 's', 'r']:
         with open('../data/possibility_dictionaries/wn_poss_dict_{}_{}.pd'.format(lang, cat), mode='w+', encoding='utf-8') as f:
            for lemma, synsets in lang2cat2lemma2fun[lang][cat].items():
                print((lemma, synsets), file=f)

def read_possibility_dictionary(path):
    from ast import literal_eval
    lemma_cat2fun = dict()
    print(path)
    with open(path, mode='r', encoding='utf-8') as f:
        for l in f:
            val, funs = literal_eval(l)
            lemma_cat2fun[val] = funs
    return lemma_cat2fun


if __name__ == '__main__':
    lang2cat2lemma2fun = generate_possibility_dictionary()
    print('Created dict')
    write_possibility_dictionary(lang2cat2lemma2fun)
    print('Printed dict')
    print('Done.')
