#!/usr/bin/env bash
#UDGold langs: Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Autoparsed langs: Bul Dut Eng Fin Fre Hin Swe
#WN langs Bul Chi Eng Fin Fre Ita Spa Swe
#GF langs Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Test langs Bul Eng Fin Fre Swe
PYTHONIOENCODING="UTF-8"
unigram_opts="-f2 -p1"
run_em () {
if [ ! -d $2 ]; then
mkdir -p "${2}"
cat ${1}/*/1_splits.txt | sort -k2 | python merge_counts.py | sort -k1,1nr > "${2}/1_splits.txt"
cat ${2}/1_splits.txt | awk '{print $2}' | while read split
do
echo $split
deprel=$(echo $split | awk -v FS='_' '{print $2}')
cat ${1}/*/${split}.txt.gz |
zcat |
python wn_em.py $3|
awk -v OFS=$'\t' '{print $NF, $0, var}' var="${deprel}" |
sort -k1,1 -k2,2gr |
cut -f2- -d $'\t' > $2/${split}.probs
done
fi
}
combine_probs () {
if [ ! -f $2 ]; then
python combine_probs.py $1 > $2 
fi
}
recount_no_deprel () {
if [ ! -f $2 ]; then
awk -v FS='\t' 'OFS="\t" {if (NF==4) {print $1, $2, $3} else {print $1,$2}}' $1 | sort -T tmp_sort_file -k2 | python merge_counts.py -f > $2
fi
}

#echo "GF UD Gold"
#run_em ../data/em_data/gf_udgold ../results/gf_udgold
#echo "WN UD Gold"
#run_em ../data/em_data/wn_udgold ../results/wn_udgold
echo "GF Parsed th50"
run_em ../data/em_data/gf_autoparsed_th50 ../results/gf_autoparsed_th50
combine_probs ../results/gf_autoparsed_th50/ ../results/gf_autoparsed_th50.probs
recount_no_deprel ../results/gf_autoparsed_th50.probs ../results/gf_nodep_autoparsed_th50.probs

echo "Unigram GF Parsed th50"
run_em ../data/em_data/gf_uni_autoparsed_th50 ../results/gf_uni_autoparsed_th50 "${unigram_opts}"
combine_probs ../results/gf_uni_autoparsed_th50/ ../results/gf_uni_autoparsed_th50.probs
recount_no_deprel ../results/gf_uni_autoparsed_th50.probs ../results/gf_uni_nodep_autoparsed_th50.probs

echo "Unigram WN Parsed th50"
run_em ../data/em_data/wn_uni_autoparsed_th50 ../results/wn_uni_autoparsed_th50 "${unigram_opts}"
combine_probs ../results/wn_uni_autoparsed_th50/ ../results/wn_uni_autoparsed_th50.probs
recount_no_deprel ../results/wn_uni_autoparsed_th50.probs ../results/wn_uni_nodep_autoparsed_th50.probs


echo "WN Parsed th50"
run_em ../data/em_data/wn_autoparsed_th50 ../results/wn_autoparsed_th50
combine_probs ../results/wn_autoparsed_th50/ ../results/wn_autoparsed_th50.probs
recount_no_deprel ../results/wn_autoparsed_th50.probs ../results/wn_nodep_autoparsed_th50.probs




echo "Noeng WN Parsed th50"
#mkdir ../data/em_data/no_eng_wn_parsed
#for lang in ../data/em_data/wn_autoparsed_th50/*
#do
#ln -s $lang ../data/em_data/no_eng_wn_parsed/$(basename $lang)
#done
#rm ../data/em_data/no_eng_wn_parsed/eng
#run_em ../data/em_data/no_eng_wn_parsed ../results/no_eng_wn_parsed

echo "Only eng WN Parsed th50"
#mkdir ../data/em_data/only_eng_wn_parsed
#ln -s ../data/wn_autoparsed_th50/eng ../data/em_data/only_eng_wn_parsed/eng
#run_em ../data/em_data/only_eng_wn_parsed ../results/only_eng_wn_parsed

echo "Unigram GF UD-GOLD"
#run_em ../data/em_data/gf_uni_udgold ../results/gf_uni_udgold "${unigram_opts}"

echo "GF Parsed th10"
#run_em ../data/em_data/gf_autoparsed_th10 ../results/gf_autoparsed_th10
echo "WN Parsed th10"
#run_em ../data/em_data/wn_autoparsed_th10 ../results/wn_autoparsed_th10
