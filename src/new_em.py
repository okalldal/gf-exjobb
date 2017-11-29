from itertools import product
from collections import defaultdict
import logging

class EM:

    def __init__(self, poss_dict_by_lang_and_ngram_position,
                 fun_vocab_size_by_position,
                 word_vocab_size_by_lang_and_position,
                 counts_by_lang,
                 ngrams_by_lang,
                 convergence_threshold=1e-5):
        self.poss_dict_by_lang_and_ngram_position = poss_dict_by_lang_and_ngram_position
        self.fun_vocab_size_by_position = fun_vocab_size_by_position
        self.word_vocab_size_by_lang_and_position = word_vocab_size_by_lang_and_position
        self.counts_by_lang = counts_by_lang
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
        logging.info('Starting new iteration')
        self.init_new_counters()
        for s in range(self.langs):
            logging.debug('Language: {}'.format(s))
            for count, ngram in zip(self.counts_by_lang[s], self.ngrams_by_lang[s]):
                logging.debug('Count, ngram: {}, {}'.format(count,ngram))
                self.update_counts(s, count, ngram)
                logging.debug('new_fun_ngram_counts: {}'.format(self.new_fun_ngram_counts))
                logging.debug('new_fun_by_lang_and_position: {}'.format(self.new_fun_by_lang_and_position))
                logging.debug('new_word_conditionals: {}'.format(self.new_word_conditionals))
        convergence_diff = self.get_convergence_diff()
        self.save_counters()
        return convergence_diff

    def update_counts(self, lang, count, ngram):
        fun_ngrams = self.possible_fun_ngrams(lang, ngram)
        logging.debug("Possible ngrams: {}".format(fun_ngrams))
        joint_probs = [self.get_fun_ngram_count(fun_ngram) * self.get_ngram_conditional(ngram, fun_ngram, lang) for
                       fun_ngram in fun_ngrams]
        logging.debug("Joint probs: {}".format(joint_probs))
        total_prob = sum(joint_probs)
        fun_ngram_probs = [prob / total_prob for prob in
                           joint_probs]  # =P(Y|X) = \phi_{si.}*\pi / (\sum_k \phi_{sik}*\pi_k
        for i, fun_ngram in enumerate(fun_ngrams):
            expected_count = count * fun_ngram_probs[i]
            logging.debug("Updateing: {}, {}, {}".format(expected_count,ngram,fun_ngram))
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
            fun_conditional_index = self.poss_dict_by_lang_and_ngram_position[lang][ngram_position][word].index(fun)
            probability = probability*self.word_conditionals[lang][ngram_position][word][fun_conditional_index]\
                          /self.fun_by_lang_and_position[lang][ngram_position][fun]
        return probability

    def update_fun_ngram_counts(self, fun_ngram, expected_count):
        if fun_ngram not in self.new_fun_ngram_counts.keys():
            self.new_fun_ngram_counts[fun_ngram] = expected_count
        else:
            self.new_fun_ngram_counts[fun_ngram] = self.new_fun_ngram_counts[fun_ngram] + expected_count

    def update_word_conditionals(self, lang, ngram, fun_ngram, expected_count):
        for ngram_position, fun in enumerate(fun_ngram):
            word = ngram[ngram_position]
            fun_conditional_index = self.poss_dict_by_lang_and_ngram_position[lang][ngram_position][word].index(fun)
            self.new_word_conditionals[lang][ngram_position][word][fun_conditional_index] = \
                    self.new_word_conditionals[lang][ngram_position][word][fun_conditional_index] + expected_count

            self.new_fun_by_lang_and_position[lang][ngram_position][fun] = \
                    self.new_fun_by_lang_and_position[lang][ngram_position][fun] + expected_count


    def init_counters(self):
        self.word_conditionals = [[[[1]*len(possibilities) for possibilities in pd]
                                       for pd in pd_by_position]
                                      for pd_by_position in self.poss_dict_by_lang_and_ngram_position]
        self.fun_by_lang_and_position = [[[1]*fun_vocab_size
                                              for fun_vocab_size in self.fun_vocab_size_by_position]
                                             for _ in range(self.langs)]
        self.fun_ngram_counts = defaultdict(lambda : 1)


    def init_new_counters(self):
        self.new_word_conditionals = [[[[0] * len(possibilities) for possibilities in pd]
                                   for pd in pd_by_position]
                                  for pd_by_position in self.poss_dict_by_lang_and_ngram_position]
        self.new_fun_by_lang_and_position = [[[0] * fun_vocab_size
                                          for fun_vocab_size in self.fun_vocab_size_by_position]
                                         for _ in range(self.langs)]
        self.new_fun_ngram_counts = dict()


    def save_counters(self):
        self.word_conditionals = self.new_word_conditionals
        self.fun_by_lang_and_position = self.new_fun_by_lang_and_position
        self.fun_ngram_counts = self.new_fun_ngram_counts


    def get_convergence_diff(self):
        return max(abs(self.new_fun_ngram_counts[fun]-self.fun_ngram_counts[fun]) for fun in self.new_fun_ngram_counts.keys())


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
    logging.basicConfig(level=logging.INFO)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', nargs='+', help='parts of speech column wise')
    parser.add_argument('-l', nargs='+', help='languages in order of input')
    parser.add_argument('-d', type=str, required=True, help='path to folder with possibility dictionaries')
    args = parser.parse_args()
    position2pos = args.p
    parts_of_speech = set(args.p)
    pd_path=args.d
    langs = args.l
    n_gram_order=len(parts_of_speech)

    poss_dicts_by_lang_and_pos = list()
    fun2id_by_pos = {pos : dict() for pos in parts_of_speech}
    id2fun_by_pos = {pos : list() for pos in parts_of_speech}
    current_fun_id_by_pos = {pos : 0 for pos in parts_of_speech}
    word2id_by_pos_and_lang = [{pos : dict() for pos in parts_of_speech} for _ in range(len(langs))]
    id2word_by_pos_and_lang = [{pos : list() for pos in parts_of_speech} for _ in range(len(langs))]
    current_word_id_by_pos_and_lang = [{pos : 0 for pos in parts_of_speech} for _ in range(len(langs))]
    current_lang=0
    for s, lang in enumerate(langs):
        poss_dicts_by_pos = {pos : list() for pos in parts_of_speech}
        with open(pd_path+"/"+lang+".txt", mode='r', encoding="utf-8") as file:
            for line in file:
                l_split = line.strip('\n').split('\t')
                word = l_split[0]
                pos = l_split[1]
                funs = l_split[2:]
                if pos in parts_of_speech:
                    fun_ids=[]

                    for fun in funs:
                        if fun not in fun2id_by_pos[pos].keys():
                            fun2id_by_pos[pos][fun] = current_fun_id_by_pos[pos]
                            id2fun_by_pos[pos].append(fun)
                            current_fun_id_by_pos[pos] = current_fun_id_by_pos[pos] + 1

                        fun_ids.append(fun2id_by_pos[pos][fun])

                    if word in word2id_by_pos_and_lang[s][pos].keys():
                        raise Exception("Word in possdict not unique: {} in {}".format(word, lang))
                    word2id_by_pos_and_lang[s][pos][word]=current_word_id_by_pos_and_lang[s][pos]
                    id2word_by_pos_and_lang[s][pos].append(word)
                    current_word_id_by_pos_and_lang[s][pos]=current_word_id_by_pos_and_lang[s][pos] + 1

                    fun_ids.sort()
                    poss_dicts_by_pos[pos].append(fun_ids)


        poss_dicts_by_lang_and_pos.append(poss_dicts_by_pos)
    poss_dicts_by_lang_and_position = \
        [[poss_dicts_by_lang_and_pos[lang][pos] for pos in position2pos] for lang in range(len(langs))]
    current_fun_id_by_position = [current_fun_id_by_pos[pos] for pos in position2pos]
    current_word_id_by_lang_and_position = \
        [[current_word_id_by_pos_and_lang[lang][pos] for pos in position2pos] for lang in range(len(langs))]

    import sys

    if sys.stdin.__next__().strip('\n') != '---':
        print('Input must start with ---', file=sys.stderr)
        exit(1)
    
    n_grams_by_lang = []
    counts_by_lang = []
    
    ngrams = []
    counts = []
    current_lang = 0
    for l in sys.stdin:
        if l.strip('\n') == '---': #new language
            current_lang = current_lang + 1
            n_grams_by_lang.append(ngrams)
            counts_by_lang.append(counts)
            ngrams = []
            counts = []
        else:
            l_split = l.strip('\n').split('\t')
            counts.append(int(l_split[0]))
            words = l_split[1:n_gram_order+1]
            word_ids = []
            for position, word in enumerate(words):
                pos = position2pos[position]
                word_ids.append(word2id_by_pos_and_lang[current_lang][pos][word])
            ngrams.append(tuple(word_ids))

        n_grams_by_lang.append(ngrams)
        counts_by_lang.append(counts)

    print(current_fun_id_by_position, file=sys.stderr)
    print(current_word_id_by_lang_and_position, file=sys.stderr)
    em = EM(poss_dicts_by_lang_and_position, current_fun_id_by_position, current_word_id_by_lang_and_position, counts_by_lang,n_grams_by_lang)
    em.run()
    em_probs = em.fun_ngram_counts
    for fun, probability in em_probs.items():
        print(*([probability] + list(fun)), sep='\t')

