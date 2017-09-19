from collections import Counter
from ast import literal_eval
import em
import analysis

def count_occurences_from_file(file_name):
    with open(file_name+'.data', encoding='utf8') as file:
        return Counter(frozenset(literal_eval(line.strip())) for line in file)

def print_probabilities(file_name, probabilities):
    with open(file_name+'.probs', 'w+', encoding='utf8') as file:
        for possibility, probability in probabilities.items():
            file.write(str(possibility) + '\t' + str(probability) + '\n')

def run_pipeline(series_name, languages):
    language_file_names = [language +'-'+ series_name for language in languages]

    language_occurences = [count_occurences_from_file(file) for file in language_file_names]
    combined_occurences = sum(language_occurences, Counter())
    print('Finished reading files and counting')

    probDict = [em.run(occurences) for occurences in language_occurences]
    combined_probDict = em.run(combined_occurences)

    print("Finished EM.")

    probability_dictionary = dict(zip(language_file_names, probDict))
    for file_name, probabilities in probability_dictionary.items():
        print_probabilities(file_name, probabilities)
    print_probabilities(series_name, combined_probDict)

    print("Finished printing probabilities.")

    analysis.run_analysis(probability_dictionary, combined_probDict)

if __name__ == "__main__":
    unigram_series_name = 'unigram-nouns'
    bigram_series_name = 'bigram-nouns'
    languages = ['en', 'sv', 'bg']

    print('Running unigram series')
    run_pipeline(unigram_series_name, languages)
    print('Running bigram series')
    run_pipeline(bigram_series_name, languages)