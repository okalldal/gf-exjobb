DIR=semeval
NUM=10000

# UNIGRAM
python semeval.py \
  --probs nodep_wn_autoparsed_th50_uni \
  --num $NUM \
  --model unigram > $DIR/unigram.key
python semeval.py \
  --probs nodep_no_eng_wn_autoparsed_th50_uni \
  --num $NUM \
  --model unigram > $DIR/unigram_no_eng.key
python semeval.py \
  --probs nodep_only_eng_wn_autoparsed_th50_uni \
  --model unigram > $DIR/unigram_only_eng.key

# BIGRAM
python semeval.py \
  --probs nodep_wn_autoparsed_th50 \
  --num $NUM \
  --model bigram > $DIR/bigram.key

python semeval.py \
  --probs nodep_no_eng_wn_autoparsed_th50 \
  --num $NUM \
  --model bigram > $DIR/bigram_no_eng.key

python semeval.py \
  --probs nodep_only_eng_wn_autoparsed_th50 \
  --num $NUM \
  --model bigram > $DIR/bigram_only_eng.key

# BIGRAM DEPREL
python semeval.py \
  --probs wn_autoparsed_th50 \
  --deprel \
  --num $NUM \
  --model bigram > $DIR/bigramdeprel.key

python semeval.py \
  --probs no_eng_wn_autoparsed_th50 \
  --deprel \
  --num $NUM \
  --model bigram > $DIR/bigramdeprel_no_eng.key

python semeval.py \
  --probs only_eng_wn_autoparsed_th50 \
  --deprel \
  --num $NUM \
  --model bigram > $DIR/bigramdeprel_only_eng.key

# INTERPOLATION
python semeval.py \
  --probs nodep_wn_autoparsed_th50 \
  --num $NUM \
  --model interpolation > $DIR/interpolation.key

python semeval.py \
  --probs nodep_no_eng_wn_autoparsed_th50 \
  --num $NUM \
  --model bigram > $DIR/interpolation_no_eng.key

python semeval.py \
  --probs nodep_only_eng_wn_autoparsed_th50 \
  --num $NUM \
  --model bigram > $DIR/interpolation_only_eng.key

# BIGRAM DEPREL
python semeval.py \
  --probs wn_autoparsed_th50 \
  --deprel \
  --num $NUM \
  --model bigram > $DIR/interpolationdeprel.key

python semeval.py \
  --probs no_eng_wn_autoparsed_th50 \
  --deprel \
  --num $NUM \
  --model bigram > $DIR/interpolationdeprel_no_eng.key

python semeval.py \
  --probs only_eng_wn_autoparsed_th50 \
  --deprel \
  --num $NUM \
  --model bigram > $DIR/interpolationdeprel_only_eng.key


