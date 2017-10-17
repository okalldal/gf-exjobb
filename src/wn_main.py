import wn_em
import logging
from itertools import product
from tqdm import tqdm


def print_probabilities(file, probabilities):
    for possibility, probability in probabilities.items():
        print(possibility, probability, sep='\t', file=file)


def parse_counts(feature_count_file, poss_dict, count_col, feature_cols, delimiter='\t'):
    counts = dict()
    for l in tqdm(feature_count_file):
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

def parse_multigram_counts(feature_count_file, unigram_poss_dict, count_col, multigram_feature_cols, delimiter='\t', root_symbol=None):
    counts = dict()
    multigram_poss_dict = dict()
    multigram_funs = set()
    unigram_poss_dict[None] = [None]
    if root_symbol:
        unigram_poss_dict[root_symbol] = ['ROOT']
    for l in tqdm(feature_count_file):
        l_split = l.strip('\n').split(delimiter)
        count = int(l_split[count_col])

        multigram_features = [tuple([l_split[i] for i in feature_cols]) for feature_cols in multigram_feature_cols]
        mf = tuple([features if features in unigram_poss_dict.keys() else None for features in multigram_features])

        counts[mf] = counts[mf] + count if mf in counts.keys() else count
        possible_multigram_funs = list(product(*[unigram_poss_dict[features] for features in mf]))
        multigram_funs.update(possible_multigram_funs)
        multigram_poss_dict[mf] = possible_multigram_funs
    return list(counts.items()), multigram_poss_dict, multigram_funs




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    languages = ['Eng', 'Swe', 'Bul', 'Fin']  # , 'Fre']

    feature_count_files = {
    lang: '../data/feature_counts/UD_gold_counts/fixed/{}_train_features.txt'.format(lang.lower()) for lang in
    languages}
    feature_count_col = -1
    feature_cols = [[0, 2], [4, 6]]
    root_symbol = ('_ROOT_', '_ROOT_')

    poss_dict_files = {lang: '../data/possibility_dictionaries/wn/wn_poss_dict_cat_{}.pd'.format(lang.lower()) for lang
                       in languages}
    poss_dict_keys = 2
    output_file = '../results/wn_multigram_probs_autoparsed.probs'

    poss_dicts = dict()
    funs = []
    word_counts = dict()
    for lang in languages:
        print(lang)
        with open(poss_dict_files[lang], mode='r', encoding='utf8') as file:
            pd, f = read_possibility_dictionary(file, key_cols=poss_dict_keys)
            poss_dicts[lang] = pd
        print('Finished reading possdict')
        with open(feature_count_files[lang], mode='r', encoding='utf8') as file:
            wc, pd, f = parse_multigram_counts(file, poss_dicts[lang], count_col=feature_count_col,
                                               multigram_feature_cols=feature_cols, root_symbol=root_symbol)
            word_counts[lang] = wc
            poss_dicts[lang] = pd
            funs.append(f)
    # print(poss_dicts)
    # poss_dicts = {'Eng' : {'bank' : ['bank.n.1', 'bank.n.2']}, 'Swe':{'bank':['bank.n.1', 'bank.n.2'], 'hypotek':['bank.n.1'], 'flodkant':['bank.n.2']}}
    # funs = ['bank.n.1', 'bank.n.2']
    # word_counts={'Eng' : [('bank', 4)], 'Swe':[('bank',3), ('hypotek',1),('flodkant',2)]}
    funs = set.union(*funs)
    probs = wn_em.run(word_counts, funs, poss_dicts)
    print('done')
    with open(output_file, mode='w+', encoding='utf8') as f:
        print_probabilities(f, probs)

