import pgf
import sys
import logging
import argparse
from itertools import takewhile, repeat
from collections import defaultdict
from scipy import log
from utils import Memoize, read_probs


@Memoize
def gf_labels():
    with open('../data/Lang.labels') as f:
        rows = [l.strip().split() for l in f if l.strip() != '']
    labels = defaultdict(lambda: ['head'])
    for row in rows:
        fun, *rest = row
        args = takewhile(lambda w: w[0:2] != '--', rest)
        labels[fun] = list(args)
    return labels


def find_heads(expression, prev_heads = [], label='root'):
    labels = gf_labels()
    fun, arguments = expression.unpack()
    arg_labels = labels[fun]
    headi = arg_labels.index('head')
    if (len(arguments) <= headi):
        return [(fun, prev_heads, label)], fun
    else:
        out, head = find_heads(arguments[headi], prev_heads, label)
        for i, arg in enumerate(arguments):
            if i != headi:
                cur_label = arg_labels[i] if len(arg_labels) > i else label
                tuples, _ = find_heads(arg, [head] + prev_heads, cur_label)
                out.extend(tuples)
        return out, head


def tree_prob(tree_tuples, bigramprobs, unigramprobs, unigram_fallback=True):
    total = 0
    bigram_count = 0
    unigram_count = 0
    for node, head in tree_tuples:
        bigram_prob = bigramprobs[(node, head)]
        unigram_prob = unigramprobs[node]

        if bigram_prob != 0:
            logging.debug("({},{}): {}".format(node, head, bigram_prob))
            bigram_count += 1
            prob = log(bigram_prob) - log(unigramprobs[head])
        elif unigram_fallback and unigram_prob != 0:
            logging.debug("({},): {}".format(node, unigram_prob))
            unigram_count += 1
            prob = log(unigram_prob)
        else:
            logging.debug("{} no collected data".format(node))
            prob = 0

        total = total-prob

    msg = 'Generated tree probability with %d bigrams and %d unigrams'
    logging.debug(msg % (bigram_count, unigram_count))
    return total

def rerank(sentence, lgr, bigramprobs, unigramprobs):
    try:
        p = lgr.parse(sentence)
    except pgf.ParseError as ex:
        logging.error(ex)
        return []

    for i, (p, ex) in enumerate(p):
        if i > 1000:
            break
        logging.debug('GF tree: ' + str(ex))
        tuples, _ = find_heads(ex)
        bigrams = [(n, hs[0] if hs else 'ROOT') for n, hs, l in tuples]
        rerank = tree_prob(bigrams, bigramprobs, unigramprobs)
        yield {'parser_prob': p, 'rerank_prob': rerank, 'bigrams': bigrams, 'expr': ex}

def run(sentences, answers, parseLang, translateLang, show_trees, niter, grammar, *args, **kwargs):
    total_tests = 0
    success = 0
    lgr = grammar.languages[parseLang]

    for i, sentence in enumerate(sentences):
        concr = grammar.languages[translateLang]
        logging.debug('=================================')
        logging.debug('Parsing sentence: ' + sentence)
        rerank_probs = []
        expr = []
        print(sentence)
        print('Correct\tParser\tRerank\tTotal\tTranslation')
        for j, result in enumerate(rerank(sentence, lgr, *args, **kwargs)):
            rerank_probs.append(result['rerank_prob'])
            expr.append(str(result['expr']))
            if j < niter:
                result['trans'] = concr.linearize(result['expr'])
                result['total'] = result['parser_prob'] + result['rerank_prob']
                result['correct'] = '✓' if answers[i] and answers[i] == str(result['expr']) else ''
                if show_trees:
                    print('{correct}\t{parser_prob}\t{rerank_prob}\t{total}\t{trans}\t{expr}'
                        .format(**result))
                else:
                    print('{correct}\t{parser_prob}\t{rerank_prob}\t{total}\t{trans}'
                        .format(**result))
        print('')

        if answers[i] and answers[i] in expr:
            total_tests += 1
            rerank_index = expr.index(answers[i])
            if all(rerank_probs[rerank_index] <= el for el in rerank_probs):
                success += 1
    
    print('===================================')
    print('Success on {} out of {} sentences where the correct sentence was found (total {} sentences)'
        .format(success, total_tests, len(sentences)))



def init(grammar_file, bigram_file, unigram_file):
    # GF
    grammar = pgf.readPGF(grammar_file)
    # bigram
    # filter out non bigram probabilities, sometimes we get these
    bigramprobs = defaultdict(lambda: 0, ((t, p) for (t, p) in read_probs(bigram_file) 
                                           if len(t) == 2 ))
    # unigram
    with open(unigram_file) as f:
        data = (l.strip().split('\t') for l in f)
        unigramprobs = defaultdict(lambda: 0, ((t, float(p)) for (t, p) in data))
    return grammar, bigramprobs, unigramprobs


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('file',
        nargs='?', 
        type=argparse.FileType(mode='r', encoding='utf-8'), 
        default=sys.stdin,
        help='file with sentences on each row')
    parser.add_argument('--unigram', '-u'
        nargs=1, 
        metavar='PROB_FILE', 
        default='../results/prasanth_counts_total_unigram.probs',
        help='file with unigram probabilities')
    parser.add_argument('--bigram', '-b' 
        nargs=1, 
        metavar='PROB_FILE',
        default='../results/prasanth_counts_total.probs',
        help='file with bigram probabilities')
    parser.add_argument('--grammar', '-g'
        nargs=1,
        metavar='PGF_FILE',
        default='../data/TranslateEngSwe.pgf',
        help='Portable grammar file from GF')
    parser.add_argument('--language', '-l',
        nargs=1,
        metavar='LANG',
        type=lambda s: 'Translate' + s
        choices={'Swe', 'Eng', 'Hin', 'Fin', 'Bul', 'Fre', 'Dut'},
        default='Eng',
        help='The language of the input sentences'
    )
    parser.add_argument('--verbose', '-v',
        action='store_true',
        help='print debug messages')
    parser.add_argument('--nparses', '-n',
        nargs=1,
        metavar='N',
        type=int,
        help='generate the top N parses from GF (default=10)',
        default=[10])
    parser.add_argument('--trees', '-t', 
        action='store_true',
        help='show the generated GF trees')
    parser.add_argument('--translate', 
        nargs=1,
        metavar='LANG', 
        type = lambda s: 'Translate' + s,
        choices={'Swe', 'Eng', 'Hin', 'Fin', 'Bul', 'Fre', 'Dut'}, 
        help='linearize the sentences into this language',
        default='Swe')

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    nparses = args.nparses[0]

    with args.file as f:
        input_data = [l.strip().split('\t') for l in f]
        sentences = [s[0] for s in input_data]
        answers   = [s[1] if len(s) > 1 else None for s in input_data]
        run(sentences, answers, args.language, args.translate, args.trees, nparses, *init(args.grammar, args.bigram, args.unigram)) 