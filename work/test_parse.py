import parse
import pgf

if __name__ == '__main__':
    ud_path = "../data/UD_English/en-ud-dev.conllu"
    out_path = "parse_test.data"
    #graphs = parse.parse_conllu_file(ud_path)
    #uni_counter, bi_counter = parse.count_features(graphs, parse.test_unigram_feature_generator,
    #                                               parse.test_bigram_feature_generator)
    #print(uni_counter)
    #print(bi_counter)

    grammar = pgf.readPGF('../data/Dictionary.pgf')
    eng_lang = grammar.languages['DictionaryEng']
    graphs = parse.parse_conllu_file(ud_path)
    uni_generator = parse.FeatureGenerator(eng_lang, grammar, use_bigrams=True, filter_node_categories=['NOUN'])
    uni_counter = parse.count_features(graphs, uni_generator)
    print(uni_counter.most_common(500))