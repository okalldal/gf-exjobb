from collections import Counter
from ast import literal_eval
import em

if __name__ == "__main__":

    print('Counting unigrams')
    to_set = lambda x: frozenset(literal_eval(x.strip()))
    occurencesEng = Counter(to_set(l) for l in open('en-unigram-nouns.data'))
    occurencesSwe = Counter(to_set(l) for l in open('sv-unigram-nouns.data'))
    occurencesBul = Counter(to_set(l) for l in open('bg-unigram-nouns.data'))
    occurences = occurencesBul + occurencesSwe + occurencesEng
    print('Finished reading file')
    
    probabilities = em.run(occurences)

    print("Finished EM.")
    with open('probabilities.txt', 'w+', encoding='utf8') as f:
        for poss, prob in probabilities:
            f.write(str(poss) + '\t' + str(prob) + '\n')
    print("Finished printing probabilities.txt")

    print('Counting bigrams')

    occurencesEng = Counter(to_set(l) for l in open('en-bigram-nouns.data'))
    occurencesSwe = Counter(to_set(l) for l in open('sv-bigram-nouns.data'))
    occurencesBul = Counter(to_set(l) for l in open('bg-bigram-nouns.data'))
    occurences = occurencesBul + occurencesSwe + occurencesEng

    print('Finished reading file')
    probabilities = em.run(occurences)

    print("Finished EM.")
    with open('bigrams.txt', 'w+', encoding='utf8') as f:
        for poss, prob in probabilities:
            f.write(str(poss) + '\t' + str(prob) + '\n')
    print("Finished printing bigrams.txt")