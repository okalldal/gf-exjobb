import parse

if __name__ == '__main__':
    ud_path = "UD_English/en-ud-dev.conllu"
    out_path = "parse_test.data"
    graphs = parse.parse_conllu_file(ud_path)
    uni_counter, bi_counter = parse.count_features(graphs, parse.test_unigram_feature_generator,
                                                   parse.test_bigram_feature_generator)
    print(uni_counter)
    print(bi_counter)
