#!/usr/bin/env bash
#UDGold langs: Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Autoparsed langs: Bul Dut Eng Fin Fre Hin Swe
#WN langs Bul Chi Eng Fin Fre Ita Spa Swe
#GF langs Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Test langs Bul Eng Fin Fre Swe
PYTHONENCODING="UTF-8"
EMDATADIR=../data/em_data/gf_autoparsed_th50
OUTDIR=../results/gf_autoparsed_th50
langs=$EMDATADIR/*/splits.txt

mkdir $OUTDIR
cat ${EMDATADIR}/*/splits.txt | sort -k2 | python merge_counts.py | sort -k1,1nr > "${OUTDIR}/total_splits.txt"
awk '{print $2}' "${OUTDIR}/total_splits.txt" | while read split
do
echo $split
cat ${EMDATADIR}/*/${split}.txt | cut -f 1,3- -d$'\t' | python wn_em.py > ${OUTDIR}/${split}.txt
done                                        