#!/usr/bin/env bash
mkdir th50
mkdir th100
mkdir th250
mkdir th500
for lang in bul dut eng fin fre hin swe
do
    echo $lang
    curl -o "th50/${lang}.txt" "http://old-darcs.grammaticalframework.org/~prakol/scratch/tree-disambiguation/uploads/conll17-autoparsed/${lang}-edge-lempos_th50-counts.txt"
    curl -o "th100/${lang}.txt" "http://old-darcs.grammaticalframework.org/~prakol/scratch/tree-disambiguation/uploads/conll17-autoparsed/${lang}-edge-lempos_th100-counts.txt"
    curl -o "th250/${lang}.txt" "http://old-darcs.grammaticalframework.org/~prakol/scratch/tree-disambiguation/uploads/conll17-autoparsed/${lang}-edge-lempos_th250-counts.txt"
    curl -o "th500/${lang}.txt" "http://old-darcs.grammaticalframework.org/~prakol/scratch/tree-disambiguation/uploads/conll17-autoparsed/${lang}-edge-lempos_th500-counts.txt"
done