from parse import UDNode
import spacy
import pgf
from tree_probs import Memoize, read_probs
from nltk.corpus import wordnet as wn
from collections import defaultdict

spacy_en = spacy.load('en')
probs = defaultdict(lambda: 0, read_probs('../results/bigram_filter_train_total.probs'))
uniprobs = defaultdict(lambda: 0, read_probs('../results/unigram_filter_total.probs'))
lgr = pgf.readPGF('../data/translate-pgfs/TranslateEng.pgf').languages['TranslateEng']


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
        if pred is not None:
            predictions.append(('HEAD_'+head, pred))

    for dep in lemma_as_head_bigrams:
        if dep!=lemma:
            _, pred = get_bigram_prediction(dep, lemma)
            if pred is not None:
                predictions.append(('DEP_'+head, pred))

    total_tests = len(lemma_as_dep_bigrams) + len(lemma_as_head_bigrams)
    total_success = 0
    total_loss = 0
    for _, pred in predictions:
        assert(len(pred)!=0)
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
    possible_funs_dep = [func for func, _, _ in lgr.lookupMorpho(dep)]
    possible_funs_head = [func for func, _, _ in lgr.lookupMorpho(head)]
    if len(possible_funs_head)==0 or len(possible_funs_dep)==0:
        return None, None

    else:
        total_prob_dep = [sum(
                                [probs[(dep, head)] for head in possible_funs_head]
                                ) for dep in possible_funs_dep]
        total_prob_head = [sum(
                                [probs[(dep, head)] for dep in possible_funs_dep]
                                ) for head in possible_funs_head]
        assert(len(possible_funs_head)!=0)
        assert (len(possible_funs_dep) != 0)
        assert (len(total_prob_dep) != 0)
        assert (len(total_prob_head) != 0)
        return list(zip(possible_funs_dep, total_prob_dep)), list(zip(possible_funs_head, total_prob_head))


def read_funs2wordnetid(path):
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
                yield fun, wnid
            except ValueError:
                continue



if __name__ == '__main__':
    wsd = dict([(s.offset(), s) for s in wn.all_synsets()])
    print('imported synsets')
    unambiguous = 0
    fun_not_possible = 0
    total_funs = 0
    total_examples = 0
    example_count = 0

    total_loss = 0
    total_success = 0
    total_tests = 0
    for fun, wnid in read_funs2wordnetid('../data/Dictionary.gf'):
        if wnid == 0:
            continue
        synset = wsd[wnid]
        lemma = lgr.linearize(pgf.readExpr(fun))
        total_funs = total_funs+1
        possible_funs = [func for func, _, _ in lgr.lookupMorpho(lemma)]
        if fun not in possible_funs:
            fun_not_possible = fun_not_possible+1
            continue
        elif len(possible_funs)==1:
            unambiguous = unambiguous+1
            continue
        if len(synset.examples()) != 0:
            example_count = example_count+1
        for example in synset.examples():
            total_examples = total_examples +1
            loss, success, tests, pred = evaluate_example_tree(fun, lemma, example)
            if tests>0:
                total_loss = total_loss + loss
                total_success = total_success+success
                total_tests = total_tests + tests
                if success>=len(pred):
                    print(fun)
                    print(example)
                    print(pred)





    print(total_funs,fun_not_possible,unambiguous, total_examples,example_count)
    print(total_loss,total_success,total_tests)