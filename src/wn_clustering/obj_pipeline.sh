res_path=results/obj
echo "marginalizing unigrams"
cut -f1,2 $1 | sort -k2 | python ../merge_counts.py -f > $res_path/noun.cnt
cut -f1,3 $1 | sort -k2 | python ../merge_counts.py -f > $res_path/verb.cnt
echo "calculating hypercounts"
python hyper_probs.py < $res_path/noun.cnt > $res_path/hyper_noun.probs
python hyper_probs.py < $res_path/verb.cnt > $res_path/hyper_verb.probs
echo "merging synsets"
python merge_synsets.py -c 1e-3 < $res_path/hyper_noun.probs > $res_path/merged_noun.cnt
python merge_synsets.py -c 1e-3 < $res_path/hyper_verb.probs > $res_path/merged_verb.cnt
echo "concating merge_dict"
cat $res_path/merged_noun.cnt $res_path/merged_verb.cnt| cut -f2,4 > $res_path/merged_dict.tsv
echo "calculating merged bigrams"
awk -v FS='\t' -v OFS='\t' 'NR == FNR{a[$1]=$2;next}; {for(i=1;i<=NF;i++){if ($i in a){$i=a[$i]}}};{print}' $res_path/merged_dict.tsv $1 |
sort -k2 | python ../merge_counts.py -f > $res_path/merged_bigram.cnt
echo "calculating full/merged conditional probs"
cut -f2,4 $res_path/merged_noun.cnt | python reverse_possdict.py | python linearization_conditional_probs.py $res_path/noun.cnt > $res_path/noun_cond.probs
cut -f2,4 $res_path/merged_verb.cnt | python reverse_possdict.py | python linearization_conditional_probs.py $res_path/verb.cnt > $res_path/verb_cond.probs
echo "running analysis"
cat $1 | python analyze_clust_probs.py $res_path/merged_dict.tsv $res_path/merged_bigram.cnt $res_path/noun_cond.probs $res_path/verb_cond.probs > $res_path/new_cnt.cnt
