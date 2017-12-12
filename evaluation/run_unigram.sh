echo wn_autoparsed >> results/wn_unigram.txt
python unigram.py -n 100000 \
  --probs ../results/nodep_wn_autoparsed_th50_uni.cnt \
  >> results/wn_unigram.txt 2>> results/wn_unigram.debug

echo no_eng_wn_autoparsed >> results/wn_unigram.txt
python unigram.py -n 100000 \
  --probs ../results/nodep_no_eng_wn_autoparsed_th50_uni.cnt \
  >> results/wn_unigram.txt 2>> results/wn_unigram.debug

echo only_eng_wn_autoparsed >> results/wn_unigram.txt
python unigram.py -n 100000 \
  --probs ../results/nodep_only_eng_wn_autoparsed_th50_uni.cnt \
  >> results/wn_unigram.txt 2>> results/wn_unigram.debug
