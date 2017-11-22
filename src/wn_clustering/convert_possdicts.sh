for dict in $2/*
do
awk -v FS='\t' -v OFS='\t' 'NR == FNR{a[$1]=$2;next}; {for(i=1;i<=NF;i++){if ($i in a){$i=a[$i]}}};{print}' $1 $dict |
python remove_duplicates.py > $3/$(basename $dict)
done
