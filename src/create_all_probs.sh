#!/bin/bash
[ $# -eq 0 ] || [ $# -eq 1 ] && { echo "Usage: $0 counts-dir out-dir"; exit 1; }
DIR=$(cd "$(dirname $0)" && pwd)
PATH=$1
PROBDIR=$2


if [ ! -f $PROBDIR/bigram_deprel.probs ]; then
  echo "generate bigram with deprel"
  python $DIR/combine_probs.py $PATH > $PROBDIR/bigram_deprel.probs
fi 

if [ ! -f $PROBDIR/bigram.probs ]; then
  echo "generate bigram"
  cut -f 1-3 $PROBDIR/bigram_deprel.probs | python $DIR/merge_counts.py -f \
    > $PROBDIR/bigram.probs
fi

if [ ! -f $PROBDIR/unigram_deprel.probs ]; then
  echo "generate unigram with deprel"
  cut -f 1,2,4 $PROBDIR/bigram_deprel.probs | python $DIR/merge_counts.py -f \
    > $PROBDIR/unigram_deprel.probs
fi

if [ ! -f $PROBDIR/unigram.probs ]; then
  echo "generate unigram"
  cut -f 1,2 $PROBDIR/unigram_deprel.probs | python $DIR/merge_counts.py -f \
    > $PROBDIR/unigram.probs
fi
