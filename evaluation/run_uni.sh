NUM=$1

# GF ==========================================================
echo "gf_uni_udgold"
python unigram.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/gf_uni_udgold_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "gf_uni_autoparsed_th50"
python unigram.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/gf_uni_autoparsed_th50_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "no_eng_gf_uni_udgold"
python unigram.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/no_eng_gf_uni_udgold_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "no_eng_gf_uni_autoparsed_th50"
python unigram.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/no_eng_gf_uni_autoparsed_th50_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "only_eng_gf_uni_udgold"
python unigram.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/only_eng_gf_uni_udgold_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "only_eng_gf_uni_autoparsed_th50"
python unigram.py \
  --possdict ../data/possibility_dictionaries/gf/eng.txt \
  --dict gf \
  --probs ../results/only_eng_gf_uni_autoparsed_th50_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

# WN ============================================================

echo "wn_uni_udgold"
python unigram.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/wn_uni_udgold_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "wn_uni_autoparsed_th50"
python unigram.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/wn_uni_autoparsed_th50_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "no_eng_wn_uni_udgold"
python unigram.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/no_eng_wn_uni_udgold_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "no_eng_wn_uni_autoparsed_th50"
python unigram.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/no_eng_wn_uni_autoparsed_th50_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "only_eng_wn_uni_udgold"
python unigram.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/only_eng_wn_uni_udgold_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM

echo "only_eng_wn_uni_autoparsed_th50"
python unigram.py \
  --possdict ../data/possibility_dictionaries/wn/eng.txt \
  --dict wn \
  --probs ../results/only_eng_wn_uni_autoparsed_th50_nodep.cnt \
  --sentence-answer ../../trainomatic/en_egs.tsv \
  --num $NUM
