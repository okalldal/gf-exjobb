echo "Lang  Total Ambiguous"
for dict in dict_files/*
do
lang=$(basename $dict)
tot_count=$(sort $dict -k1,2 | uniq -f1,2 | wc -l)
#tot_unique=$(uniq -u -f 1 $dict | wc -l)
tot_amb=$(sort $dict -k1,2 | uniq -d -f1,2 | wc -l)
echo "${lang%.txt} $tot_count  $tot_amb"
done | sort -k2,2nr
