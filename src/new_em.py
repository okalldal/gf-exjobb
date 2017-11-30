from itertools import product
from collections import defaultdict
from math import log
import sys


class EM:

    def __init__(self, poss_dict_by_lang_and_ngram_position,
                 counts_by_lang,
                 ngrams_by_lang,
                 convergence_threshold=1e-5):
        self.poss_dict_by_lang_and_ngram_position = poss_dict_by_lang_and_ngram_position
        self.counts_by_lang = counts_by_lang
        self.total_counts = sum([sum(counts) for counts in counts_by_lang])
        self.ngrams_by_lang = ngrams_by_lang
        self.langs = len(poss_dict_by_lang_and_ngram_position)
        self.positions = len(poss_dict_by_lang_and_ngram_position[0])
        self.convergence_threshold=convergence_threshold
        self.word_conditionals = None
        self.fun_by_lang_and_position = None
        self.fun_ngram_counts = None
        self.init_counters()
        self.new_word_conditionals = None
        self.new_fun_by_lang_and_position = None
        self.new_fun_ngram_counts = None

    def run(self):
        iterations = 0
        convergence_diff = 0
        while iterations < 2 or convergence_diff >= self.convergence_threshold:
            convergence_diff = self.do_em_iteration()
            iterations = iterations + 1

    def do_em_iteration(self):
        self.init_new_counters()
        for s in range(self.langs):
            for count, ngram in zip(self.counts_by_lang[s], self.ngrams_by_lang[s]):
                self.update_counts(s, count, ngram)
        convergence_diff = self.get_convergence_diff()
        self.save_counters()
        return convergence_diff

    def update_counts(self, lang, count, ngram):
        fun_ngrams = list(self.possible_fun_ngrams(lang, ngram))
        joint_probs = [self.get_fun_ngram_count(fun_ngram) * self.get_ngram_conditional(ngram, fun_ngram, lang) for
                       fun_ngram in fun_ngrams]
        total_prob = sum(joint_probs)
        fun_ngram_probs = [prob / total_prob for prob in
                           joint_probs]  # =P(Y|X) = \phi_{si.}*\pi / (\sum_k \phi_{sik}*\pi_k
        for i, fun_ngram in enumerate(fun_ngrams):
            expected_count = count * fun_ngram_probs[i]
            self.update_fun_ngram_counts(fun_ngram, expected_count)
            self.update_word_conditionals(lang, ngram, fun_ngram, expected_count)

    def possible_fun_ngrams(self, lang, ngram):
        return product(*[poss_dict[word] for word, poss_dict in zip(ngram,self.poss_dict_by_lang_and_ngram_position[lang])])

    def get_fun_ngram_count(self, fun_ngram):
        return self.fun_ngram_counts[fun_ngram]

    def get_ngram_conditional(self, ngram,fun_ngram,lang):
        probability = 1
        for ngram_position, fun in enumerate(fun_ngram):
            word = ngram[ngram_position]
            probability = probability*self.word_conditionals[lang][ngram_position][word][fun]\
                          /self.fun_by_lang_and_position[lang][ngram_position][fun]
        return probability

    def update_fun_ngram_counts(self, fun_ngram, expected_count):
        self.new_fun_ngram_counts[fun_ngram] = self.new_fun_ngram_counts[fun_ngram] + expected_count

    def update_word_conditionals(self, lang, ngram, fun_ngram, expected_count):
        for ngram_position, fun in enumerate(fun_ngram):
            word = ngram[ngram_position]
            self.new_word_conditionals[lang][ngram_position][word][fun] = \
                    self.new_word_conditionals[lang][ngram_position][word][fun] + expected_count

            self.new_fun_by_lang_and_position[lang][ngram_position][fun] = \
                    self.new_fun_by_lang_and_position[lang][ngram_position][fun] + expected_count


    def init_counters(self):
        self.word_conditionals = [[defaultdict(lambda : defaultdict(lambda : 1))
                                       for _ in range(self.positions)]
                                      for _ in range(self.langs)]
        self.fun_by_lang_and_position = [[defaultdict(lambda : 1)
                                          for _ in range(self.positions)]
                                         for _ in range(self.langs)]
        self.fun_ngram_counts = defaultdict(lambda : 1)


    def init_new_counters(self):
        self.new_word_conditionals = [[defaultdict(lambda: defaultdict(lambda: 0))
                                   for _ in range(self.positions)]
                                  for _ in range(self.langs)]
        self.new_fun_by_lang_and_position = [[defaultdict(lambda: 0)
                                          for _ in range(self.positions)]
                                         for _ in range(self.langs)]
        self.new_fun_ngram_counts = defaultdict(lambda: 0)


    def save_counters(self):
        self.word_conditionals = self.new_word_conditionals
        self.fun_by_lang_and_position = self.new_fun_by_lang_and_position
        self.fun_ngram_counts = self.new_fun_ngram_counts


    def get_convergence_diff(self):
        return sum(self.new_fun_ngram_counts[fun]*log(self.new_fun_ngram_counts[fun]/self.fun_ngram_counts[fun])
                   for fun in self.new_fun_ngram_counts.keys()
                   if self.fun_ngram_counts[fun]>1e-10 and self.new_fun_ngram_counts[fun]>1e-10)/self.total_counts


class EMPossibility:
    def __init__(self, id, words, funs, fun_conditionals):
        self.id = id
        self.words = words
        self.funs = funs
        self.fun_conditionals = fun_conditionals

class EMRecordCreater:

    def __init__(self):
        self.fun_ngram2id = dict()
        self.current_id = 0
        self.id2fun_ngram = list()

    def make_em_records(self, word_ids, poss_dicts_by_position):
        possible_fun_ngrams = product(*[poss_dict[word] for word, poss_dict in zip(word_ids,poss_dicts_by_position)])
        for fun_ngram in possible_fun_ngrams:
            if fun_ngram not in self.fun_ngram2id.keys():
                self.fun_ngram2id[fun_ngram]=self.current_id
                self.id2fun_ngram.append(fun_ngram)
                current_id = current_id + 1
            conditionals = tuple(poss_dicts_by_position[i][word_ids[i]].index(fun) for i, fun in enumerate(fun_ngram))
            yield EMPossibility(self.fun_ngram2id[fun_ngram],word_ids,fun_ngram,conditionals)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', nargs='+', help='parts of speech column wise')
    parser.add_argument('-l', nargs='+', help='languages in order of input')
    parser.add_argument('-d', type=str, required=False, help='path to folder with possibility dictionaries')
    parser.add_argument('-o', type=int,
                        help='Ngram order',
                        default=2)
    parser.add_argument('-f', type=int, help='Number of features', default=2)
    args = parser.parse_args()

    if args.d:
        position2pos = args.p
        parts_of_speech = set(args.p)
        pd_path=args.d
        langs = args.l
        n_gram_order=len(parts_of_speech)

        poss_dicts_by_lang_and_pos = list()
        for s, lang in enumerate(langs):
            poss_dicts_by_pos = {pos : dict() for pos in parts_of_speech}
            with open(pd_path+"/"+lang+".txt", mode='r', encoding="utf-8") as file:
                for line in file:
                    l_split = line.strip('\n').split('\t')
                    word = l_split[0]
                    pos = l_split[1]
                    funs = l_split[2:]
                    if pos in parts_of_speech:
                        if word in poss_dicts_by_pos[pos].keys():
                            poss_dicts_by_pos[pos][word] = list(set(poss_dicts_by_pos[pos][word]+funs))
                        else:
                            poss_dicts_by_pos[pos][word]=funs
            poss_dicts_by_lang_and_pos.append(poss_dicts_by_pos)
        poss_dicts_by_lang_and_position = \
            [[poss_dicts_by_lang_and_pos[lang][pos] for pos in position2pos] for lang in range(len(langs))]



    if sys.stdin.__next__().strip('\n') != '---':
        print('Input must start with ---', file=sys.stderr)
        exit(1)
    
    n_grams_by_lang = []
    counts_by_lang = []
    
    ngrams = []
    counts = []
    current_lang = 0
    em_data_poss_dicts_by_lang_and_position = []
    poss_dicts = [defaultdict(list) for _ in range(args.o)]
    for l in sys.stdin:
        if l.strip('\n') == '---': #new language
            current_lang = current_lang + 1
            n_grams_by_lang.append(ngrams)
            counts_by_lang.append(counts)
            em_data_poss_dicts_by_lang_and_position.append(poss_dicts)
            ngrams = []
            counts = []
            poss_dicts = [defaultdict(list) for _ in range(args.o)]
        else:
            l_split = l.strip('\n').split('\t')
            counts.append(int(l_split[0]))
            words = []
            for i in range(1,1+args.o*args.f,args.o):
                words.append(tuple(l_split[i:i+args.o]))
            for i in range(args.o):
                for j in range(1+args.o * args.f+i, len(l_split), args.o):
                    fun = l_split[j]
                    if fun not in poss_dicts[i][words[i]]:
                        poss_dicts[i][words[i]].append(fun)
            ngrams.append(tuple(words))

    n_grams_by_lang.append(ngrams)
    counts_by_lang.append(counts)
    em_data_poss_dicts_by_lang_and_position.append(poss_dicts)
    em = EM(em_data_poss_dicts_by_lang_and_position, counts_by_lang, n_grams_by_lang)
    em.run()
    em_probs = em.fun_ngram_counts
    for fun, probability in em_probs.items():
        print(*([probability] + list(fun)), sep='\t')

