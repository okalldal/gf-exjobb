#!/usr/bin/env bash
#UDGold langs: Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Autoparsed langs: Bul Dut Eng Fin Fre Hin Swe
#WN langs Bul Chi Eng Fin Fre Ita Spa Swe
#GF langs Bul Chi Dut Eng Fin Fre Ger Hin Ita Spa Swe
#Test langs Bul Eng Fin Fre Swe
PYTHONIOENCODING="UTF-8"
gold_options="-l 8 -c 7 -s 2,3,6 -f 0:2,4:6" #UD Gold
parsed_options="-l 6 -c 0 -s 2,3,5 -f 1:2,4:5" #Autoparsed
gold_uni_options="-l 8 -c 7 -s 2,3 -f 0:2" #UD Gold
parsed_uni_options="-l 6 -c 0 -s 2,3 -f 1:2" #Autoparsed
wn_gf_pd_dir="../data/possibility_dictionaries/gf_wn"
wn_pd_dir="../data/possibility_dictionaries/wn2"
gf_pd_dir="../data/possibility_dictionaries/gf/"
kras_pd_dir="../data/possibility_dictionaries/kras/"
gold_count_dir="../data/feature_counts/UD_gold_counts"
parsed_count_dir="../data/feature_counts/autoparsed"
out_dir="../data/em_data/wn_udgold"

make_em_data () {
for file in $(comm -12 <(ls $1) <(ls $2))
do
if [ ! -d $3/${file%.*} ]; then
echo $3/${file%.*}
mkdir -p $3/${file%.*}
python ../src/make_em_data.py $4 -o $3/${file%.*} -p $1/$file $1/$file < $2/$file
gzip -9r $3/${file%.*}
gzip -d $3/${file%.*}/1_splits.txt.gz
fi
done
}

make_em_data $gf_pd_dir $gold_count_dir ../data/em_data/gf_udgold "${gold_options}"
make_em_data $gf_pd_dir $gold_count_dir ../data/em_data/gf_udgold_uni "${gold_uni_options}"

make_em_data $wn_gf_pd_dir $gold_count_dir ../data/em_data/wn_udgold "${gold_options}"
make_em_data $wn_gf_pd_dir $gold_count_dir ../data/em_data/wn_udgold_uni "${gold_uni_options}"

make_em_data $kras_pd_dir $gold_count_dir ../data/em_data/kras_udgold "${gold_options}"
make_em_data $kras_pd_dir $gold_count_dir ../data/em_data/kras_udgold_uni "${gold_uni_options}"

make_em_data $gf_pd_dir $parsed_count_dir/th050 ../data/em_data/gf_autoparsed_th50 "${parsed_options}"
make_em_data $gf_pd_dir $parsed_count_dir/th050 ../data/em_data/gf_autoparsed_th50_uni "${parsed_uni_options}"

make_em_data $wn_gf_pd_dir $parsed_count_dir/th050 ../data/em_data/wn_autoparsed_th50 "${parsed_options}"
make_em_data $wn_gf_pd_dir $parsed_count_dir/th050 ../data/em_data/wn_autoparsed_th50_uni "${parsed_uni_options}"

make_em_data $kras_pd_dir $parsed_count_dir/th050 ../data/em_data/kras_autoparsed_th50 "${parsed_options}"
make_em_data $kras_pd_dir $parsed_count_dir/th050 ../data/em_data/kras_autoparsed_th50_uni "${parsed_options}"

