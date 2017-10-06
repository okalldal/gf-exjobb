from possibility_dictionary_generation import read_possibility_dictionary, get_funs_from_gf_dictionary
from collections import defaultdict, Counter


def unlinearizable_funs(funs, possibility_dictionary):
    return set(possibility_dictionary['__NOLINEARIZATION__']).intersection(funs)


def unambiguous_funs(funs, possibility_dictionary):
    return_funs = set()
    for possibility in possibility_dictionary.keys():
        possible_funs = [fun for fun in possibility_dictionary[possibility] if fun in funs]
        if possibility != '__NOLINEARIZATION__' and len(possible_funs)==1:
            return_funs.add(possible_funs[0])
    return return_funs

def partition_functions_by_connectivity(funs, possibility_dicts):

    ###Make a dictionary showing all language/lemma/category linearizations each function can have
    funs2langlemmacat = dict([(fun, [])for fun in funs])
    #For each language
    for lang in possibility_dicts.keys():
        #For each lemma/cat in language
        for lemma_cat in possibility_dicts[lang].keys():
            ##Add language and lemmacat for each possible function
            for possible_fun in possibility_dicts[lang][lemma_cat]:
                if possible_fun in funs:
                    funs2langlemmacat[possible_fun].append((lang, lemma_cat))


    for fun in funs2langlemmacat.keys():
        assert(len(funs2langlemmacat[fun])==len(lang_names))

    ### Make a graph where each function is a node and each node is connected if those functions are ever in the same possibility set
    fun_connections = dict([(fun, set())for fun in funs])
    for fun in funs:
        #get all possibility sets of the function
        for lang, lemma_cat in funs2langlemmacat[fun]:
            #for all functions in the possibility set
            for poss_fun in possibility_dicts[lang][lemma_cat]:
                if poss_fun in funs and fun != poss_fun:
                    fun_connections[fun].add(poss_fun)
    for key in fun_connections.keys():
        assert(key in funs)
        if not len(fun_connections[key])>0:
            print(key)
            print(fun_connections[key])
        assert(len(fun_connections[key])>0)
        for val in fun_connections[key]:
            assert(val != key)
            assert(val in funs)
    ##Find connected components
    funs_left = set(funs)
    disjoint_sets = []
    while len(funs_left)>0:
        start_fun = funs_left.pop()
        visited_funs = set([start_fun])
        seen_unvisited_funs = fun_connections[start_fun]
        assert(start_fun not in seen_unvisited_funs)
        while len(seen_unvisited_funs)>0:
            current_fun = seen_unvisited_funs.pop()
            assert(current_fun != start_fun)
            funs_left.remove(current_fun)
            visited_funs.add(current_fun)
            new_funs = fun_connections[current_fun]-visited_funs
            assert(new_funs.issubset(funs_left))
            seen_unvisited_funs.update(new_funs)
        disjoint_sets.append(visited_funs)
    return disjoint_sets


if __name__ == '__main__':
    lang_names = ['TranslateBul',
                        #'TranslateDut',
                        #'TranslateEng',
                        'TranslateFin',
                        'TranslateFre',
                        'TranslateGer',
                        'TranslateHin',
                        'TranslateIta',
                        'TranslateSpa',
                        'TranslateSwe']
    lang_dicts=dict()
    for lang in lang_names:
        lang_dicts[lang] = read_possibility_dictionary('../results/poss_dict_{}.pd'.format(lang))

    all_funs = set(get_funs_from_gf_dictionary('../data/Dictionary.gf'))
    print(len(all_funs))
    linearizable_all = all_funs
    for lang in lang_names:
        print(lang, len(unlinearizable_funs(all_funs,lang_dicts[lang])))
        linearizable_all = linearizable_all - unlinearizable_funs(all_funs,lang_dicts[lang])
    print(len(linearizable_all))
    unambiguous_all = linearizable_all
    ambiguous_all = linearizable_all
    for lang in lang_names:
        print(lang, len(unambiguous_funs(linearizable_all,lang_dicts[lang])))
        ambiguous_all = ambiguous_all.intersection(linearizable_all-unambiguous_funs(linearizable_all,lang_dicts[lang]))
        unambiguous_all = unambiguous_all.intersection(unambiguous_funs(linearizable_all,lang_dicts[lang]))

    ambiguous_any = linearizable_all - unambiguous_all
    print(len(ambiguous_any))
    print(len(ambiguous_all))
    print(list(ambiguous_all))

    partitions = partition_functions_by_connectivity(ambiguous_any, lang_dicts)

    print(len(partitions))
    print(Counter([len(part)for part in partitions]))


