NUM=20000

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
