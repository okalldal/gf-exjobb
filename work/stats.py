from collections import Counter
import numpy as np

def convert_possibilities_to_ids(occurences):
    occurency_tuples = []
    possibility2id = dict()
    id2possibility = []
    current_id = 0
    for occurency, count in dict(occurences).items():
        possibility_ids = []
        for possibility in occurency:
            if possibility not in possibility2id.keys():
                possibility2id[possibility] = current_id
                id2possibility.append(possibility)
                possibility_ids.append(current_id)
                current_id = current_id + 1
            else:
                possibility_ids.append(possibility2id[possibility])
        if len(possibility_ids) > 0:
            occurency_tuples.append((possibility_ids, count))
    return occurency_tuples, id2possibility, possibility2id


def em_algorithm(occurrence_tuples, init_probs, convergence_threshold):
    """occurrence_tuples : [([int],int)], init_probs : np.[double], convergence_threshold : double"""
    convergence_diff = convergence_threshold
    current_probs = init_probs
    total_counts = sum([count for _, count in occurrence_tuples])
    while convergence_diff >= convergence_threshold:
        new_probs = np.zeros(current_probs.shape)
        for possibilities, count in occurrence_tuples:
            possibility_probabilities = current_probs[possibilities]  # numpy advanced indexing
            total_probability = np.sum(possibility_probabilities)
            new_probs[possibilities] = new_probs[possibilities] + possibility_probabilities*count/total_probability
        prob_quotients = new_probs / current_probs
        threshold_mask = np.abs(prob_quotients) > 1e-50*total_counts    # used for numpy advanced indexing to remove differences
                                                                # caused by numerical imprecision
        convergence_diff = np.sum(new_probs[threshold_mask]*np.log(prob_quotients[threshold_mask]))/total_counts
        current_probs = new_probs
        print(convergence_diff)
    return current_probs


def make_unigram_probabilities(all_functions_with_categories, function_counts, function2id):
    category_counts = dict()
    smoothed_counts = np.zeros([len(all_functions_with_categories)])
    i = -1
    for function_name, category in all_functions_with_categories:

        i = i + 1
        if function_name in function2id.keys():
            smoothed_counts[i] = function_counts[function2id[function_name]] + 1
        else:
            smoothed_counts[i] = 1

        if category not in category_counts.keys():
            category_counts[category] = 1
        else:
            category_counts[category] = category_counts[category] + 1

    i = -1
    total_smoothed_count = np.sum(smoothed_counts)
    for function_name, _ in all_functions_with_categories:
        i = i + 1
        yield (function_name, smoothed_counts[i]/total_smoothed_count)
    for category, count in category_counts.items():
        yield (category, count)


def make_bigram_probabilities(bigram_counts, id2bigram):
    total_counts = np.sum(bigram_counts)
    for bigram, count in zip(id2bigram, list(bigram_counts)):
        yield (bigram, count/total_counts)


UD_FILE = '../data/UD_English-r1.3/en-ud-train.conllu'

from ast import literal_eval
import gf_funs
def run():
    runUnigram = False
    runBigram = True
    if runUnigram:
        print('Counting unigrams')
        to_set = lambda x: frozenset(literal_eval(x.strip()))
        occurencesEng = Counter(to_set(l) for l in open('en-unigram-nouns.data'))
        occurencesSwe = Counter(to_set(l) for l in open('sv-unigram-nouns.data'))
        occurencesBul = Counter(to_set(l) for l in open('bg-unigram-nouns.data'))
        occurences = occurencesBul + occurencesSwe + occurencesEng
        #occurences = occurencesEng

        print('Finished reading file')
        occurency_tuples, id2possibility, poss2id = convert_possibilities_to_ids(occurences)
        with open('ids.txt', 'w+') as f:
            for poss in id2possibility:
                f.write(str(poss) + '\n')
        print("Converted possibilities to id.")
        del occurences
        #id2possibility = dict(zip(possibility2id.values(), possibility2id.keys()))
        #possibilities = [id2possibility[i] for i in range(len(id2possibility))]
        #del possibility2id
        #del id2possibility
        #"Compiled possibility list"

        print(len(occurency_tuples))
        em_vals = em_algorithm(occurency_tuples, np.ones([len(id2possibility)])/1e10, 1e-5)
        probabilities = make_unigram_probabilities(gf_funs.functions, em_vals, poss2id)
        print("Finished EM.")
        with open('probabilities.txt', 'w+', encoding='utf8') as f:
            for poss, prob in probabilities:
                f.write(str(poss) + '\t' + str(prob) + '\n')
        print("Finished printing.")
    
    if runBigram:
        print('Counting bigrams')
        to_set = lambda x: frozenset(literal_eval(x.strip()))
        occurencesEng = Counter(to_set(l) for l in open('en-bigram-nouns.data'))
        occurencesSwe = Counter(to_set(l) for l in open('sv-bigram-nouns.data'))
        occurencesBul = Counter(to_set(l) for l in open('bg-bigram-nouns.data'))
        occurences = occurencesBul + occurencesSwe + occurencesEng
        #occurences = occurencesEng

        print('Finished reading file')
        occurency_tuples, id2possibility, poss2id = convert_possibilities_to_ids(occurences)
        print("Converted possibilities to id.")
        del occurences

        print('Number of occurencies: ' + str(len(occurency_tuples)))

        em_vals = em_algorithm(occurency_tuples, np.ones([len(id2possibility)])/1e10, 1e-5)
        probabilities = make_bigram_probabilities(em_vals, poss2id)
        print("Finished EM.")
        with open('probabilities.txt', 'w+', encoding='utf8') as f:
            for poss, prob in probabilities:
                f.write(str(poss) + '\t' + str(prob) + '\n')
        print("Finished printing.")

if __name__ == "__main__":
    run()
