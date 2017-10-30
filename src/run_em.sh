#!/usr/bin/env bash
#UDGold langs: Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Autoparsed langs: Bul Dut Eng Fin Fre Hin Swe
#WN langs Bul Chi Eng Fin Fre Ita Spa Swe
#GF langs Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Test langs Bul Eng Fin Fre Swe
PYTHONENCODING="UTF-8"

run_em () {
if [ ! -d $2 ]; then
mkdir -p $2
cat ${1}/*/splits.txt | sort -k2 | python merge_counts.py | sort -k1,1nr > "${2}/total_splits.txt"
awk '{print $2}' "${2}/total_splits.txt" | while read split
do
echo $split
cat ${1}/*/${split}.txt | cut -f 1,3- -d$'\t' | python wn_em.py > $2/${split}.txt
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
