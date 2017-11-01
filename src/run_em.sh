#!/usr/bin/env bash
#UDGold langs: Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Autoparsed langs: Bul Dut Eng Fin Fre Hin Swe
#WN langs Bul Chi Eng Fin Fre Ita Spa Swe
#GF langs Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Test langs Bul Eng Fin Fre Swe
PYTHONENIOCODING="UTF-8"
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
echo "GF UD Gold"
run_em ../data/em_data/gf_udgold ../results/gf_udgold
echo "WN UD Gold"
run_em ../data/em_data/wn_udgold ../results/wn_udgold
echo "GF Parsed th50"
run_em ../data/em_data/gf_autoparsed_th50 ../results/gf_autoparsed_th50
echo "GF Parsed th10"
run_em ../data/em_data/gf_autoparsed_th10 ../results/gf_autoparsed_th10
echo "noeng GF Parsed th50"
run_em ../data/em_data/noeng_gf_parsed ../results/noeng_gf_parsed
echo "Unigram GF UD-GOLD"
run_em ../data/em_data/gf_uni_udgold ../results/gf_uni_udgold "${unigram_opts}"
echo "Unigram GF Parsed th50"
run_em ../data/em_data/gf_uni_autoparsed_th50 ../results/gf_uni_autoparsed_th50 "${unigram_opts}"