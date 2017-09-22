from collections import Counter
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

def run_pipeline(languages, conllu_file_paths, grammar_files, output_path):
    language_unigram_features = []
    language_bigram_features = []
    for lang, conllu_file, grammar_file in zip(languages, conllu_file_paths, grammar_files):
        print("Parsing {}.".format(lang))
        grammar = pgf.readPGF(grammar_file)
        language_grammar = grammar.languages['Dictionary'+lang]
        unigram_feature_gen = parse.FeatureGenerator(language_grammar, grammar, use_bigrams=False)
        bigram_feature_gen = parse.FeatureGenerator(language_grammar, grammar, use_bigrams=True)
        graphs = parse.parse_conllu_file(conllu_file)
        unigram_features, bigram_features = parse.count_features(graphs, unigram_feature_gen, bigram_feature_gen)
        language_unigram_features.append(unigram_features)
        language_bigram_features.append(bigram_features)
    total_unigram_features = sum(language_unigram_features, Counter())
    total_bigram_features = sum(language_bigram_features, Counter())

    print("Finished parsing")

    print("Running unigram EM for each language.")
    language_unigram_probDicts = dict(zip(languages, [em.run(occurences) for occurences in language_unigram_features]))
    print("Running unigram EM for all languages.")
    total_unigram_probDict = em.run(total_unigram_features)
    print("Running bigram EM for each language.")
    language_bigram_probDicts = dict(zip(languages, [em.run(occurences) for occurences in language_bigram_features]))
    print("Running bigram EM for all languages.")
    total_bigram_probDict = em.run(total_bigram_features)

    print("Finished EM.")

    for lang in languages:
        print_probabilities(output_path + "unigram_"+lang, language_unigram_probDicts[lang])
        print_probabilities(output_path + "bigram_" + lang, language_bigram_probDicts[lang])
    print_probabilities(output_path + "unigram_total", total_unigram_probDict)
    print_probabilities(output_path + "bigram_total", total_bigram_probDict)

    print("Finished printing probabilities.")

    print("Analysing unigram distributions")
    analysis.run_analysis(language_unigram_probDicts, total_unigram_probDict)
    print("Analysing bigram distributions")
    analysis.run_analysis(language_bigram_probDicts, total_bigram_probDict)

if __name__ == "__main__":
    languages = ['Eng', 'Swe', 'Bul']
    conllu_files = ['../data/UD_English/en-ud-dev.conllu',
                    '../data/UD_Swedish/sv-ud-dev.conllu',
                    '../data/UD_Bulgarian/bg-ud-dev.conllu']
    grammar_files = ['../data/Dictionary.pgf']*3
    output_path = '../results/'

    run_pipeline(languages, conllu_files,grammar_files,output_path)