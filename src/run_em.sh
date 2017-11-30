#!/usr/bin/env bash

PYTHONIOENCODING="UTF-8"

unigram_opts="-f2 -p1"

run_em () {
if [ ! -f $2 ]; then
cat ${1}/*/1_splits.txt | sort -k2 | python merge_counts.py | sort -k1,1nr |
awk '{print $2}' | while read split
do
echo $split>&2
deprel=$(echo $split | awk -v FS='_' '{print $2}')
cat ${1}/*/${split}.txt.gz |
zcat |
python wn_em.py $3|
awk -v OFS=$'\t' '$1 > 0.0001 {print $0, var}' var="${deprel}"
done > $2 
fi
}

combine_probs () {
if [ ! -f $2 ]; then
totcount=numsum
python combine_probs.py $1 > $2 
fi
}

recount_no_deprel () {
if [ ! -f $2 ]; then
awk -v FS='\t' 'OFS="\t" {if (NF==4) {print $1, $2, $3} else {print $1,$2}}' ../results/$1 | sort -T tmp_sort_file -k2 | python merge_counts.py -f > $2
fi
}

em_and_recount () {
echo $1>&2
run_em ../data/em_data/$1 ../results/$1.cnt "${2}"
echo "Recount no deprel">&2
recount_no_deprel ../results/$1.cnt ../results/$1_nodep.cnt
}

no_lang_em_recount () {
mkdir ../data/em_data/no_$1_$2
for lang in ../data/em_data/$2/*
do
ln -rs $lang ../data/em_data/no_$1_$2
done
rm ../data/em_data/no_$1_$2/$1
em_and_recount no_$1_$2 "${3}"
rm -r ../data/em_data/no_$1_$2
}

only_lang_em_recount () {
mkdir ../data/em_data/only_$1_$2
ln -rs ../data/em_data/$2/$1 ../data/em_data/only_$1_$2
em_and_recount only_$1_$2 "${3}"
rm -r ../data/em_data/only_$1_$2
}

run_all () {
em_and_recount $1 "${2}"
no_lang_em_recount eng $1 "${2}"
only_lang_em_recount eng $1 "${2}"
}

run_all gf_udgold
run_all gf_uni_udgold "$unigram_opts"

run_all wn_udgold
run_all wn_uni_udgold "$unigram_opts"

run_all kras_udgold
run_all kras_uni_udgold "$unigram_opts"

run_all gf_uni_autoparsed_th50 "$unigram_opts"
run_all gf_autoparsed_th50

run_all wn_uni_autoparsed_th50 "$unigram_opts"
run_all wn_autoparsed_th50

run_all kras_uni_autoparsed_th50 "$unigram_opts"
run_all kras_autoparsed_th50

run_all clust_autoparsed_th50_uni "$unigram_opts"
run_all clust_autoparsed_th50
