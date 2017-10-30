from nltk.corpus import wordnet as wn
from tqdm import tqdm

cat_len = {'n':82115, 'v':13767, 'a':18156, 's':18156, 'r':3621}
wncat2udcat = {'n':'NOUN', 'v':'VERB', 'a':'ADJ', 's':'ADJ', 'r':'ADV'}


def generate_possibility_dictionary(languages, usecat=False):
    lang2lemma2fun = dict([(lang, dict()) for lang in languages])
    #funs = set()
    for cat in ['n', 'v', 'a', 's', 'r']:
        for synset in tqdm(wn.all_synsets(cat), total=cat_len[cat]):
            #funs.add(synset.name())
            for lang in languages:
                for lemma in synset.lemma_names(lang.lower()):
                    key = (lemma, wncat2udcat[cat]) if usecat else (lemma,)
                    if key in lang2lemma2fun[lang].keys():
                        if synset.name() not in lang2lemma2fun[lang][key]:
                            lang2lemma2fun[lang][key].append(synset.name())
                    else:
                        lang2lemma2fun[lang][key] = [synset.name()]
    return lang2lemma2fun#, funs

def write_possibility_dictionary(path, lemma2fun):
    with open(path, mode='w+', encoding='utf-8') as f:
        for key, synsets in lemma2fun.items():
            print('\t'.join(list(key)+synsets), file=f)

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
    #lang2lemma2fun, _ = generate_possibility_dictionary(wn.langs())
    #print(type(lang2lemma2fun))
    lang2lemmacat2fun = generate_possibility_dictionary(wn.langs(), usecat=True)
    print(type(lang2lemmacat2fun))
    print('Created dict')
    #for lang in wn.langs():
    #    write_possibility_dictionary('../data/possibility_dictionaries/wn2/{}.txt'.format(lang), lang2lemma2fun[lang])
    for lang in wn.langs():
        write_possibility_dictionary('../data/possibility_dictionaries/wn2/{}.txt'.format(lang), lang2lemmacat2fun[lang])
    print('Printed dict')
    print('Done.')