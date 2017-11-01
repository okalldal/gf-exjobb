#!/usr/bin/env bash
for lang in bul dut eng fin fre hin swe
do
    for thresh in th010 th050 th100 th250 th500
    do
        echo $lang $thresh
        if [ ! -f ../data/feature_counts/autoparsed/$thresh/${lang}.txt ]; then
            mkdir -p ../data/feature_counts/autoparsed/$thresh
            curl "http://old-darcs.grammaticalframework.org/~prakol/scratch/tree-disambiguation/uploads/conll17-autoparsed/${lang}-edge-lempos_${thresh}-counts.txt.gz" |
            zcat > "../data/feature_counts/autoparsed/${thresh}/${lang}.txt"
        fi
    done
done