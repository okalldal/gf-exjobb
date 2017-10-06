from collections import Counter, defaultdict
from ast import literal_eval
import em
import analysis
import parse_counts
import logging

def count_occurences_from_file(file_name):
    with open(file_name+'.data', encoding='utf8') as file:
        return Counter(frozenset(literal_eval(line.strip())) for line in file)

def print_probabilities(file_name, probabilities):
    with open(file_name+'.probs', 'w+', encoding='utf8') as file:
        for possibility, probability in probabilities.items():
            file.write(str(possibility) + '\t' + str(probability) + '\n')


def run_pipeline(languages, features):

    language_prob_dicts = dict()

    total_features = sum(list(features.values()), Counter())
    for lang in languages:
        logging.info("Running EM for {}.".format(lang))
        language_prob_dicts[lang] = em.run(features[lang])
        print_probabilities(output_path + "_" + lang, language_prob_dicts[lang])
    logging.info("Running EM for all languages.")
    total_prob_dicts = em.run(total_features)
    print_probabilities(output_path + "_total", total_prob_dicts)
    logging.info("Analysing distributions.")
    analysis.run_analysis(language_prob_dicts, total_prob_dicts)
    logging.info("Finished pipeline.")
    return language_prob_dicts, total_prob_dicts

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    languages = ['Eng', 'Swe', 'Bul']

    output_path = '../results/'
    feature_count_files = {'Eng' : '../data/feature_counts/Eng_train_features.txt',
                           'Swe': '../data/feature_counts/Swe_train_features.txt',
                           'Bul': '../data/feature_counts/Bul_train_features.txt'}

    poss_dict_files = {'Eng': '../data/possibility_dictionaries/poss_dict_TranslateEng.pd',
                        'Swe': '../data/possibility_dictionaries/poss_dict_TranslateSwe.pd',
                        'Bul': '../data/possibility_dictionaries/poss_dict_TranslateBul.pd'}

    features = parse_counts.parse_languages(languages, feature_count_files, poss_dict_files)
    run_pipeline(languages, features)