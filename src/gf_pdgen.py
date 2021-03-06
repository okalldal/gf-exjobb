GF2UD_CAT = {'N': 'NOUN',
 'PN': 'PROPN',
 'A': 'ADJ',
 'V': 'VERB',
 'V2': 'VERB',
 'V3': 'VERB',
 'VV': 'VERB',
 'VA': 'VERB',
 'VS': 'VERB',
 'VQ': 'VERB',
 'V2V': 'VERB',
 'V2A': 'VERB',
 'V2S': 'VERB',
 'V2Q': 'VERB',
 'AdA': 'ADV',
 'AdN': 'ADV',
 'AdV': 'ADV',
 'Adv': 'ADV',
 'IAdv': 'ADV',
 'Conj': 'CONJ',
 'Pron': 'PRON',
 'NP': 'PRON',
 'IP': 'PRON',
 'Predet': 'DET',
 'Det': 'DET',
 'IDet': 'DET',
 'Quant': 'DET',
 'IQuant': 'DET',
 'Interj': 'INTJ',
 'Prep': 'ADP',
 'Subj': 'ADV'}

def get_funs_from_gf_dictionary(path):
    with open(path, encoding='utf-8') as f:
        for l in f:
            l_split = l.split()
            if len(l_split) < 2 or l_split[0] != 'fun':
                continue
            yield l_split[1]


def generate_possibility_dictionary(grammar, dict_file):
    from collections import defaultdict
    lang2lemma_cat2fun = defaultdict(lambda: defaultdict(lambda: []))
    for fun in set(get_funs_from_gf_dictionary(dict_file)):
        gf_exp = pgf.readExpr(fun)
        cat = grammar.functionType(fun).cat
        for lang in grammar.languages.values():
            lemmas = list(lang.linearizeAll(gf_exp))
            if lang.hasLinearization(fun) and len(lemmas) > 0:
                lemmas.sort()
                lang2lemma_cat2fun[lang.name][(lemmas[0], cat)].append(fun)
            else:
                lang2lemma_cat2fun[lang.name]['__NOLINEARIZATION__'].append(fun)
    return lang2lemma_cat2fun

def write_possibility_dictionary(lang2lemma_cat2fun):
    for lang in lang2lemma_cat2fun.keys():
        with open('../data/gf_possibility_dictionaries/{}'.format(lang), mode='w+', encoding='utf-8') as f:

            for val, funs in lang2lemma_cat2fun[lang].items():
                if val != '__NOLINEARIZATION__':
                    out = list(val) + list(funs)
                    if out[1] in GF2UD_CAT.keys():
                        out[1]=GF2UD_CAT[out[1]]
                        print(*out,sep="\t", file=f)

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
    #grammar_file = '../data/translate-pgfs/Translate11.pgf'
    #dict_file = '../data/Dictionary.gf'

    #import pgf
    #gr = pgf.readPGF(grammar_file)
    print('Read pgf')
    #lang2lemma_cat2fun = generate_possibility_dictionary(gr, dict_file)
    #del(gr)
    import os
    lang2lemma_cat2fun = dict()
    for path in os.listdir('../data/possibility_dictionaries'):
        lang2lemma_cat2fun[path] = read_possibility_dictionary('../data/possibility_dictionaries/'+path)
    print('Created dict')
    write_possibility_dictionary(lang2lemma_cat2fun)
    print('Printed dict')
    print('Done.')
