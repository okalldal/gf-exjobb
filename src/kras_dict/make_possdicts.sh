#! bin/bash
cat subset.csv | python plid2synset.py > panlex2wnid.tsv
mkdir dict_files
cat lang_dict.txt |
while read id code
do
awk -v FS='\t' -v OFS='\t' -v lang=$id 'NR == FNR{a[$1]=$3;next}; {for (i=3;i<=NF;i+=3) {if ($i==lang) {print $(i+1),a[$1], $1}}}' panlex2wnid.tsv wordnet.tsv |
sort -k1,2 | python ../merge_dict.py > dict_files/$code.txt
done
