

awk -v FS='\t' -v OFS='\t' 'BEGIN{a["ROOT"]="ROOT"};NR == FNR{a[$1]=$2;next};{print $1, a[$2],a[$3],$4}' $1 $2
