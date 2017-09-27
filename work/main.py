from collections import Counter, defaultdict
from ast import literal_eval
import em
import analysis
import parse
import pgf
import logging

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
            logging.info("Running {} EM for {}.".format(series, lang))
            language_prob_dicts[series][lang] = em.run(features[series][lang])
            print_probabilities(output_path + series+"_" + lang, language_prob_dicts[series][lang])
        logging.info("Running {} EM for all languages.".format(series))
        total_prob_dicts[series] = em.run(total_features[series])
        print_probabilities(output_path + series + "_total", total_prob_dicts[series])
        logging.info("Analysing {} distributions.".format(series))
        analysis.run_analysis(series, language_prob_dicts[series], total_prob_dicts[series])
        logging.info("Finished pipeline.")
    return language_prob_dicts, total_prob_dicts

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    languages = ['Eng', 'Swe', 'Bul', 'Dut', 'Fin', 'Fre', 'Ger', 'Ita', 'Spa']
    conllu_files_dev = {'Eng': '../data/UD_English/en-ud-dev.conllu',
                    'Swe': '../data/UD_Swedish/sv-ud-dev.conllu',
                    'Bul': '../data/UD_Bulgarian/bg-ud-dev.conllu',
                    'Chi': '../data/UD_Chinese/zh-ud-dev.conllu',
                    'Dut': '../data/UD_Dutch/nl-ud-dev.conllu',
                    'Fin': '../data/UD_Finnish/fi-ud-dev.conllu',
                    'Fre': '../data/UD_French/fr-ud-dev.conllu',
                    'Ger': '../data/UD_German/de-ud-dev.conllu',
                    'Hin': '../data/UD_Hindi/hi-ud-dev.conllu',
                    'Ita': '../data/UD_Italian/it-ud-dev.conllu',
                    'Spa': '../data/UD_Spanish/es-ud-dev.conllu'
                    }
    conllu_files_train = {'Eng': '../data/UD_English/en-ud-train.conllu',
                    'Swe': '../data/UD_Swedish/sv-ud-train.conllu',
                    'Bul': '../data/UD_Bulgarian/bg-ud-train.conllu',
                    'Chi': '../data/UD_Chinese/zh-ud-train.conllu',
                    'Dut': '../data/UD_Dutch/nl-ud-train.conllu',
                    'Fin': '../data/UD_Finnish/fi-ud-train.conllu',
                    'Fre': '../data/UD_French/fr-ud-train.conllu',
                    'Ger': '../data/UD_German/de-ud-train.conllu',
                    'Hin': '../data/UD_Hindi/hi-ud-train.conllu',
                    'Ita': '../data/UD_Italian/it-ud-train.conllu',
                    'Spa': '../data/UD_Spanish/es-ud-train.conllu'
                    }
    grammar_files = dict([(lang, '../data/translate-pgfs/Translate{}.pgf'.format(lang)) for lang in languages])
    grammar_language_names = dict([(lang, 'Translate{}'.format(lang)) for lang in languages])
    output_path = '../results/'

    series = ['bigram_filter']
    generators = {'unigram' : parse.FeatureGenerator(None, None, use_bigrams=False, filter_possible_functions=False),
                  'bigram': parse.FeatureGenerator(None, None, use_bigrams=True, filter_possible_functions=False),
                  'unigram_filter': parse.FeatureGenerator(None, None, use_bigrams=False, filter_possible_functions=True),
                  'bigram_filter': parse.FeatureGenerator(None, None, use_bigrams=True, filter_possible_functions=True),
                  'bigram_filter_nvaa': parse.FeatureGenerator(None, None, use_bigrams=True,
                                                               filter_possible_functions=True,
                                                               filter_node_categories=['NOUN', 'VERB', 'ADJ', 'ADV'],
                                                               filter_feature_categories=['NOUN', 'VERB', 'ADJ', 'ADV']),
                  'trigram_filter': parse.FeatureGenerator(None, None, use_trigrams=True, filter_possible_functions=True)}

    features = parse.parse_languages_with_generators(languages, series, conllu_files_train, grammar_files,
                                                     grammar_language_names, generators)
    run_pipeline(languages, series, features)