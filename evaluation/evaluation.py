import spacy
import pgf
import trainomatic
from utils import Memoize, read_probs
from nltk.corpus import wordnet as wn
from collections import defaultdict
from itertools import chain
import logging


def evaluate_example_tree(true_fun, lemma, sentence):
    doc = spacy_en(sentence)
    lemma_as_dep_bigrams = [word.head.lemma_ for word in doc if word.lemma_ == lemma]
    lemma_as_head_bigrams = [word.lemma_ for word in doc if word.head.lemma_ == lemma]
    predictions = []
    for head in lemma_as_dep_bigrams:
        if head==lemma:
            pred, _ = get_bigram_prediction(lemma, 'ROOT')
        else:
            pred, _ = get_bigram_prediction(lemma, head)
        if pred is not None and len(pred) > 0 :
            predictions.append(('HEAD_'+head, pred))

    for dep in lemma_as_head_bigrams:
        if dep!=lemma:
            _, pred = get_bigram_prediction(dep, lemma)
            if pred is not None and len(pred) > 0:
                predictions.append(('DEP_'+dep, pred))

    total_tests = len(lemma_as_dep_bigrams) + len(lemma_as_head_bigrams)
    total_success = 0
    total_loss = 0
    for _, pred in predictions:
        if (len(pred) == 0):
            continue
        true_fun_prob = 0.0
        total_prob = 0.0
        number_of_maxes = 0
        max_prob = 0.0
        for fun, prob in pred:
            if fun == true_fun:
                true_fun_prob = prob
            if prob>max_prob:
                number_of_maxes = 1
                max_prob = prob
            elif prob == max_prob:
                number_of_maxes = number_of_maxes+1
            total_prob = total_prob+prob

        success = 1/number_of_maxes if true_fun_prob==max_prob else 0
        if total_prob == 0:
            loss = 1-success
        else:
            loss = 1-true_fun_prob/total_prob
        total_success = total_success + success
        total_loss = total_loss + loss

    return total_loss, total_success, total_tests, predictions


def get_bigram_prediction(dep, head):
    possible_funs_dep = [func for func, _, _ in lgr.lookupMorpho(dep) if gr.functionType(func).cat == 'N']
    possible_funs_head = [func for func, _, _ in lgr.lookupMorpho(head) if gr.functionType(func).cat == 'N']
    if len(possible_funs_head)==0 or len(possible_funs_dep)==0:
        return None, None

    else:
        total_prob_dep = [sum(
                                [probs[(dep, head)] for head in possible_funs_head]
                                ) for dep in possible_funs_dep]
        total_prob_head = [sum(
                                [probs[(dep, head)] for dep in possible_funs_dep]
                                ) for head in possible_funs_head]

        assert (len(possible_funs_head)!=0)
        assert (len(possible_funs_dep) != 0)
        assert (len(total_prob_dep) != 0)
        assert (len(total_prob_head) != 0)

        dep = list((fun, prob) for fun, prob in zip(possible_funs_dep, total_prob_dep) if prob > 0)
        head = list((fun, prob) for fun, prob in zip(possible_funs_head, total_prob_head) if prob > 0)
        return dep, head


def read_wnid2fun(path):
    with open(path, encoding='utf-8') as f:
        for l in f:
            l_split = l.split()
            if len(l_split)==0 or l_split[0]!= 'fun':
                continue
            fun = l_split[1]
            l_splitbar = l.split('--')
            if len(l_splitbar)<2:
                continue
            try:
                wnid = int(l_splitbar[1].split()[0])
                yield wnid, fun
            except ValueError:
                continue

def wordnet_examples():
    for s in wn.all_synsets():
        for ex in s.examples():
            yield (s.offset(), ex)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Loading Spacy')
    spacy_en = spacy.load('en_depent_web_md')
    logging.info('Loading Probabilities')
    probs = defaultdict(lambda: 0, read_probs('../results/test_total.probs'))
    logging.info('Loading GF')
    gr  = pgf.readPGF('../data/translate-pgfs/TranslateEng.pgf')
    lgr = gr.languages['TranslateEng']
    logging.info('Loading GF to wordnet')
    wn2fun = defaultdict(lambda: None, read_wnid2fun('../data/Dictionary.gf'))
    logging.info('Initialization finished')

    unambiguous = 0
    fun_not_possible = 0
    total_examples = 0

    total_loss = 0
    total_success = 0
    total_tests = 0
    lemmas = {}

    sources = chain(wordnet_examples(), trainomatic.parse_dir())

    for wnid, sentence in sources:
        fun = wn2fun[wnid]
        if not fun:
            continue
        
        total_examples += 1
        lemma = lgr.linearize(pgf.readExpr(fun))
        possible_funs = [func for func, _, _ in lgr.lookupMorpho(lemma)]

        if fun not in possible_funs:
            fun_not_possible += 1
            continue
        elif len(possible_funs)==1:
            unambiguous += 1
            continue
        
        loss, success, tests, pred = evaluate_example_tree(fun, lemma, sentence)

        if tests>0:
            total_loss = total_loss + loss
            total_success = total_success+success
            total_tests = total_tests + tests
            if not lemma in lemmas:
                lemmas[lemma] = {'count': 0, 'success': 0, 'preds': []}
            lemmas[lemma]['count'] += len(pred)
            lemmas[lemma]['success'] += success
            lemmas[lemma]['preds'] += [pred]

    rate = [(lemma, obj['success']/obj['count'], obj) for lemma, obj in lemmas.items() if obj['count'] != 0]
    rate.sort(key=lambda t: t[1], reverse=True)
    non_zero = lambda item: [p for p in item['preds'] if sum(sum(p for _, p in x) for _, x in p)]

    logging.info('Total tests: %s', total_examples)
    logging.info('Total success: %s', total_success)

    from IPython import embed
    embed()