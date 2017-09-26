from collections import Counter, defaultdict
from ast import literal_eval
import em
import analysis
import parse
import pgf

def count_occurences_from_file(file_name):
    with open(file_name+'.data', encoding='utf8') as file:
        return Counter(frozenset(literal_eval(line.strip())) for line in file)

def print_probabilities(file_name, probabilities):
    with open(file_name+'.probs', 'w+', encoding='utf8') as file:
        for possibility, probability in probabilities.items():
            file.write(str(possibility) + '\t' + str(probability) + '\n')


def run_pipeline(languages, series_names, features):

    total_features = dict()
    language_prob_dicts = defaultdict(dict)
    total_prob_dicts = dict()
    for series in series_names:
        total_features[series] = sum(list(features[series].values()), Counter())
        for lang in languages:
            print("Running {} EM for {}.".format(series, lang))
            language_prob_dicts[series][lang] = em.run(features[series][lang])
            print_probabilities(output_path + series+"_" + lang, language_prob_dicts[series][lang])
        print("Running {} EM for all languages.".format(series))
        total_prob_dicts[series] = em.run(total_features[series])
        print_probabilities(output_path + series + "_total", total_prob_dicts[series])
        print("Analysing unigram distributions")
        analysis.run_analysis(language_prob_dicts[series], total_prob_dicts[series])
    print("Finished pipeline.")
    return language_prob_dicts, total_prob_dicts

if __name__ == "__main__":
    languages = ['Eng', 'Swe', 'Bul']
    conllu_files = {'Eng': '../data/UD_English/en-ud-dev.conllu',
                    'Swe': '../data/UD_Swedish/sv-ud-dev.conllu',
                    'Bul': '../data/UD_Bulgarian/bg-ud-dev.conllu'}
    grammar_files = defaultdict(lambda: '../data/Dictionary.pgf')
    grammar_language_names = {'Eng': 'DictionaryEng',
                               'Swe': 'DictionarySwe',
                               'Bul': 'DictionaryBul'}
    output_path = '../results/'

    series = ['unigram_filter', 'trigram_filter']
    generators = {'unigram' : parse.FeatureGenerator(None, None, use_bigrams=False, filter_possible_functions=False),
                  'bigram': parse.FeatureGenerator(None, None, use_bigrams=True, filter_possible_functions=False),
                  'unigram_filter': parse.FeatureGenerator(None, None, use_bigrams=False, filter_possible_functions=True),
                  'bigram_filter': parse.FeatureGenerator(None, None, use_bigrams=True, filter_possible_functions=True),
                  'trigram_filter': parse.FeatureGenerator(None, None, use_trigrams=True, filter_possible_functions=True)}

    features = parse.parse_languages_with_generators(languages, series, conllu_files, grammar_files,
                                                     grammar_language_names, generators)
    run_pipeline(languages, series, features)