import wn_em
import logging

def print_probabilities(file, probabilities):
    for possibility, probability in probabilities.items():
        print(possibility, probability, sep='\t', file=file)

def parse_counts(feature_count_file, poss_dict, count_col, feature_cols, delimiter='\t'):
    counts = dict()
    for l in feature_count_file:
        l_split = l.split(delimiter)
        count = int(l_split[count_col])
        feature = tuple([l_split[i] for i in feature_cols])
        if feature in poss_dict.keys():
            counts[feature] = counts[feature] + count if feature in counts.keys() else count
    return list(counts.items())

def read_possibility_dictionary(possibility_dictionary_file, key_cols=1, delimiter='\t'):
    possibilities = dict()
    all_funs = set()
    for l in possibility_dictionary_file:
        l_split = l.strip('\n').split(delimiter)
        word = tuple(l_split[:key_cols])
        funs = l_split[key_cols:]
        all_funs.update(funs)
        possibilities[word] = funs
    return possibilities, all_funs

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    languages = ['Eng', 'Swe', 'Bul', 'Cmn', 'Fin', 'Ita']

    output_path = '../results/'
    feature_count_files = {lang : '../data/feature_counts/{}_train_features.txt'.format(lang) for lang in languages}
    feature_count_files['Cmn'] = '../data/feature_counts/Chi_train_features.txt'
    poss_dict_files = {lang: '../data/wordnet_possibility_dictionaries/only_lemma/wn_poss_dict_{}.pd'.format(lang.lower()) for lang in languages}
    #poss_dict_files['Cmn'] = '../data/gf_possibility_dictionaries/poss_dict_TranslateChi.pd'
    poss_dicts = dict()
    funs = []
    word_counts=dict()
    for lang in languages:
        with open(poss_dict_files[lang], mode='r', encoding='utf8') as f:
            pd, f = read_possibility_dictionary(f)
            poss_dicts[lang] = pd
            funs.append(f)
        with open(feature_count_files[lang], mode='r', encoding='utf8') as f:
            word_counts[lang] = parse_counts(f,poss_dicts[lang],count_col=-1, feature_cols=[0])
    #poss_dicts = {'Eng' : {'bank' : ['bank.n.1', 'bank.n.2']}, 'Swe':{'bank':['bank.n.1', 'bank.n.2'], 'hypotek':['bank.n.1'], 'flodkant':['bank.n.2']}}
    #funs = ['bank.n.1', 'bank.n.2']
    #word_counts={'Eng' : [('bank', 4)], 'Swe':[('bank',3), ('hypotek',1),('flodkant',2)]}
    funs = set.union(*funs)
    probs = wn_em.run(word_counts, funs, poss_dicts)
    print('done')
    with open('test.probs', mode='w+', encoding='utf8') as f:
        print_probabilities(f, probs)

