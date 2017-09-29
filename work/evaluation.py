from parse import UDNode
import spacy
import pgf
from tree_probs import Memoize, read_probs
from nltk.corpus import wordnet as wn
import pickle
import os

#sen = spacy.load('en')
#probs = read_probs('../results/bigram_filter_total.probs')
#marginal_head = Memoize(lambda fun: sum(p for (a, b), p in probs.items() if b == fun))
#marginal_child = Memoize(lambda fun: sum(p for (a, b), p in probs.items() if a == fun))
lgr = pgf.readPGF('../data/translate-pgfs/TranslateEng.pgf').languages['TranslateEng']


def evaluate_example_tree(fun, lemma, sentence):
    doc = sen(sentence)
    lemma_as_dep_bigrams = [(word.lemma_, word.head.lemma_) for word in doc if word.lemma_ == lemma]
    lemma_as_head_bigrams = [(word.lemma_, word.head.lemma_) for word in doc if word.head.lemma_ == lemma]
    total_loss = 0
    total_tests = 0
    total_pred = 0
    faulty_predictions = []
    for lemma, head in lemma_as_dep_bigrams:
        if head==lemma:
            loss, success, = get_loss_lemma_as_dep(fun, lemma, 'ROOT')
        else:
            loss, success, prediction = get_loss_lemma_as_dep(fun, lemma, head)
        total_loss = total_loss + loss
        total_pred = total_pred + success
        total_tests = total_tests + 1
        if not success:
            faulty_predictions.append((prediction, fun))

    for lemma, dep in  lemma_as_head_bigrams    :
        if head!=lemma:
            loss, success = get_loss_lemma_as_head(fun, lemma, dep)
            total_loss = total_loss + loss
            total_pred = total_pred + success
            total_tests = total_tests + 1
            if not success:
                faulty_predictions.append((prediction, fun))
    return total_loss, total_pred, total_tests, faulty_predictions

def get_loss_lemma_as_dep(true_fun, lemma, head):
    possible_funs_lemma = [func for func, _, _ in lgr.lookupMorpho(lemma) if marginal_child(func) > 0]
    possible_funs_head = [func for func, _, _ in lgr.lookupMorpho(head) if marginal_head(func) > 0]


    total_prob_lemma = [sum([probs[(n, h)]/marginal_head(h) for h in possible_funs_head]) for n in possible_funs_lemma]
    true_fun_prob = sum([probs[(true_fun, h)]/marginal_head(h) for h in possible_funs_head])

    if true_fun_prob >= max(total_prob_lemma):
        success = 1
    else:
        success = 0
    loss = true_fun_prob/sum(total_prob_lemma)

    prediction = possible_funs_lemma[total_prob_lemma.index(min(total_prob_lemma))]
    return loss, success, prediction



def get_loss_lemma_as_head(true_fun, lemma, dep):
    possible_funs_lemma = [func for func, _, _ in lgr.lookupMorpho(lemma) if marginal_head(func) > 0]
    possible_funs_dep = [func for func, _, _ in lgr.lookupMorpho(dep) if marginal_child(func) > 0]

    total_prob_lemma = [sum([probs[(d, n)] / marginal_child(d) for d in possible_funs_dep]) for n in
                        possible_funs_lemma]
    true_fun_prob = sum([probs[(d, true_fun)] / marginal_child(d) for d in possible_funs_dep])

    if true_fun_prob >= max(total_prob_lemma):
        success = 1
    else:
        success = 0
    loss = true_fun_prob / sum(total_prob_lemma)

    prediction = possible_funs_lemma[total_prob_lemma.index(min(total_prob_lemma))]
    return loss, success, prediction

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
    total_funs = 0
    total_examples = 0
    example_count = 0
    for fun, wnid in read_funs2wordnetid('../data/Dictionary.gf'):
        if wnid == 0:
            continue
        synset = wsd[wnid]
        lemma = lgr.linearize(pgf.readExpr(fun))
        total_funs = total_funs+1
        if len(lgr.lookupMorpho(lemma))==1:
            unambiguous = unambiguous+1
            continue
        if len(synset.examples()) != 0:
            example_count = example_count+1
        for example in synset.examples():
            total_examples = total_examples +1
            evaluate_example_tree(fun, lemma, example)


    print(total_funs,unambiguous, total_examples,example_count)