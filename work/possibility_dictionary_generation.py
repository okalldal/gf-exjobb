from collections import defaultdict

def get_funs_from_gf_dictionary(path):
    with open(dict_file, encoding='utf-8') as f:
        for l in f:
            l_split = l.split()
            if len(l_split) < 2 or l_split[0] != 'fun':
                continue
            yield l_split[1]



if __name__ == '__main__':
    import pgf
    grammar_file = '../data/translate-pgfs/Translate11.pgf'
    dict_file = '../data/Dictionary.gf'
    gr = pgf.readPGF(grammar_file)
    print('Read pgf')
    lang2lemma_cat2fun = defaultdict(lambda: defaultdict(lambda: []))
    for fun in get_funs_from_gf_dictionary(dict_file):
        gf_exp = pgf.readExpr(fun)
        cat = gr.functionType(fun).cat
        for lang in gr.languages.values():
            if lang.hasLinearization(fun):
                lemma = lang.linearize(gf_exp)
                lang2lemma_cat2fun[lang.name][(lemma, cat)].append(fun)
            else:
                lang2lemma_cat2fun[lang.name]['__NOLINEARIZATION__'].append(fun)
    print('Created dict')
    for lang in gr.languages.values():
        with open('../results/poss_dict_{}.pd'.format(lang.name), mode='w+', encoding='utf-8') as f:
            for val, funs in lang2lemma_cat2fun[lang.name].items():
                print('{}:{}'.format(val, funs), file=f)
    print('Printed dict')
    print('Done.')