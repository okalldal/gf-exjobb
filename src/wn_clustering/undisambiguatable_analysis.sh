awk 'NR == FNR{a[$1]=$2".n."$3;next}; {b=$2;sub(/\.n\..*/, "",b);if (b in a && a[b]==$4){print}}' <(cut -f2,4 $1 | sed s/'\.'/$'\t'/g | cut -f1,4,6 | sort | uniq -d) $1 | sort -k3,3gr -k4 -k2,2
