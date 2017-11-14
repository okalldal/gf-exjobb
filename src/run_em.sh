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
echo $1
run_em ../data/em_data/$1 ../results/$1.cnt
echo "Recount no deprel"
recount_no_deprel ../results/$1.cnt ../results/$1_nodep.cnt
}

no_lang_em_recount () {
mkdir ../data/em_data/no_$1_$2
ln -rs ../data/$2/* ../data/em_data/no_$1_$2
rm ../data/em_data/no_$1_$2/$1
em_and_recount ../data/em_data/no_$1_$2
rm -r ../data/em_data/no_$1_$2
}

only_lang_em_recount () {
mkdir ../data/em_data/only_$1_$2
ln -rs ../data/$2/$1 ../data/em_data/only_$1_$2
em_and_recount ../data/em_data/only_$1_$2
rm -r ../data/em_data/only_$1_$2
}

em_and_recount gf_udgold
em_and_recount wn_udgold
#em_and_recount gf_autoparsed_th50
#em_and_recount wn_autoparsed_th50
#em_and_recount gf_uni_autoparsed_th50
#em_and_recount wn_uni_autoparsed_th50

