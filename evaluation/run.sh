NUM=$1

echo "clust_autoparsed_th50"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn_clust/eng.txt \
  --dict wn \
  --deprel \
  --probs ../results/clust_autoparsed_th50.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/wnids_clust5 \
  --num $NUM 

echo "clust_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn_clust/eng.txt \
  --dict wn \
  --probs ../results/clust_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/wnids_clust5 \
  --num $NUM 

echo "gf_udgold_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/gf_udgold_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "gf_udgold"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --deprel \
  --probs ../results/gf_udgold.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "no_eng_gf_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/no_eng_gf_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "no_eng_gf_autoparsed_th50"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --deprel \
  --probs ../results/no_eng_clust_autoparsed_th50.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "only_eng_gf_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/only_eng_gf_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "only_eng_gf_autoparsed_th50"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --deprel \
  --probs ../results/only_eng_clust_autoparsed_th50.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "wn_udgold"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --deprel \
  --probs ../results/wn_udgold.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "wn_autoparsed_th50"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --deprel \
  --probs ../results/wn_autoparsed_th50.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "only_eng_wn_autoparsed_th50"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --deprel \
  --probs ../results/only_eng_wn_autoparsed_th50.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "no_eng_wn_autoparsed_th50"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --deprel \
  --probs ../results/no_eng_wn_autoparsed_th50.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "gf_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/gf_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "gf_autoparsed_th50"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --deprel \
  --probs ../results/gf_autoparsed_th50.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "wn_udgold_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/wn_udgold_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "wn_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/wn_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "only_eng_wn_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/only_eng_wn_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "no_eng_wn_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/no_eng_wn_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "kras_udgold_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/kras_udgold_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "no_eng_kras_udgold_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/no_eng_kras_udgold_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "only_eng_kras_udgold_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/only_eng_kras_udgold_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "kras_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/kras_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "no_eng_kras_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/no_eng_kras_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

echo "only_eng_kras_autoparsed_th50_nodep"
python quantitative.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/only_eng_kras_autoparsed_th50_nodep.cnt \
  --sentence-data ../../trainomatic/en.conllu \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM 

