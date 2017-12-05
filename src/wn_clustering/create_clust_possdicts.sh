#!/usr/bin/env bash
# this script assumes nodep_wn_autoparsed_th50_uni.cnt are already calculated with the em pipeline
bash generate_hyper_dict.sh ../../results/nodep_wn_autoparsed_th50_uni.cnt 1e-5 > hyper_dict.tsv
mkdir ../../data/possibility_dictionaries/clust_wn
bash convert_possdicts.sh hyper_dict.tsv ../../data/possibility_dictionaries/wn ../../data/possibility_dictionaries/clust_wn