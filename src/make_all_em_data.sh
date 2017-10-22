#!/usr/bin/env bash
#UDGold langs: Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Autoparsed langs: Bul Dut Eng Fin Fre Hin Swe
#WN langs Bul Chi Eng Fin Fre Ita Spa Swe
#GF langs Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Test langs Bul Eng Fin Fre Swe
PYTHONENCODING="UTF-8"
UD_GOLD_OPTIONS="-l 8 -c 7 -s 2,3,6 -f 0:2,4:6"
AUTOPARSED_OPTIONS="-l 6 -c 0 -s 2,3,5 -f 1:2,4:5"
mkdir ../data/em_data

echo "WN UD-gold-counts"
mkdir ../data/em_data/wn_udgold
for lang in bul chi eng fin fre ita spa swe
do
echo $lang
DICT_FILE="../data/possibility_dictionaries/wn/${lang}.txt"
COUNT_FILE="../data/feature_counts/UD_gold_counts/${lang}.txt"
OUT_PATH="../data/em_data/wn_udgold/${lang}"
mkdir $OUT_PATH
python ../src/make_em_data.py $UD_GOLD_OPTIONS -o $OUT_PATH -p $DICT_FILE $DICT_FILE < $COUNT_FILE
done

mkdir ../data/em_data/gf_udgold
echo "GF UD-gold-counts"
for lang in bul chi dut eng fin fre ger hin ita spa swe
do
echo $lang
DICT_FILE="../data/possibility_dictionaries/gf/${lang}.txt"
COUNT_FILE="../data/feature_counts/UD_gold_counts/${lang}.txt"
OUT_PATH="../data/em_data/gf_udgold/${lang}"
mkdir $OUT_PATH
python ../src/make_em_data.py $UD_GOLD_OPTIONS -o $OUT_PATH -p $DICT_FILE $DICT_FILE < $COUNT_FILE
done

mkdir ../data/em_data/wn_autoparsed_th50
echo "WN autoparsed"
for lang in bul eng fin fre swe
do
echo $lang
DICT_FILE="../data/possibility_dictionaries/wn/${lang}.txt"
COUNT_FILE="../data/feature_counts/autoparsed/th50/${lang}.txt"
OUT_PATH="../data/em_data/wn_autoparsed_th50/${lang}"
mkdir $OUT_PATH
python ../src/make_em_data.py $AUTOPARSED_OPTIONS -o $OUT_PATH -p $DICT_FILE $DICT_FILE < $COUNT_FILE
done

mkdir ../data/em_data/gf_autoparsed_th50
echo "GF autoparsed"
for lang in bul dut eng fin fre hin swe
do
echo $lang
DICT_FILE="../data/possibility_dictionaries/gf/${lang}.txt"
COUNT_FILE="../data/feature_counts/autoparsed/th50/${lang}.txt"
OUT_PATH="../data/em_data/gf_autoparsed_th50/${lang}"
mkdir $OUT_PATH
python ../src/make_em_data.py $AUTOPARSED_OPTIONS -o $OUT_PATH -p $DICT_FILE $DICT_FILE < $COUNT_FILE
done
