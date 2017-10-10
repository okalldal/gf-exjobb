#!/bin/bash

TAB=`echo -e "\t"`
#SORT_OPTS="-S 50% --parallel=8 -T $PWD/tmp";
SORT_OPTS="-S 50% -T $PWD/tmp"
export LC_ALL=C

TMP="$PWD/tmp"
if [[ ! -d "${TMP}" ]] ; then
    mkdir -p "${TMP}";
fi

transformer1="tr '[:upper:]' '[:lower:]'"
transformer2="awk '{print tolower($0)}'"

MORPH_TAGGED=true
if $MORPH_TAGGED ; then 
    BUFFER="$TMP/$$.morphbuffer"
    bzcat $1 | grep -v -e "^#" -e "^$" | \
	cut -f2,3,4,6 | \
	awk '{print tolower($1)"\t"$2"\t"$3"\t"$4;}' | \
	head -n 1000000 \
	> $BUFFER
else
    BUFFER="$TMP/$$.tagsbuffer"
    bzcat $1 | grep -v -e "^#" -e "^$" | \
	cut -f2,4 | \
	awk '{print tolower($1)"\t"$2;}' | \
	head -n 1000000 \
	> $BUFFER
fi

# lower-cased surface forms
cat $BUFFER | \
    awk '{print $1"\t"$3;}' | \
    sort $SORT_OPTS -k1 | uniq -c | \
    sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
    sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.vcb"

cat "$2.vcb" | \
    sort $SORT_OPTS -k2,3 --stable -t"$TAB" | \
    awk -F'\t' '
{ 
    if(key!=""$2) {
	print count"\t"key"\t"value; count=$1; key=""$2; value=""$3;
    } else {
	value=value":::"$3; count+=$1;
    } 
}' | \
    sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.taglex"

if $MORPH_TAGGED ; then
    cat $BUFFER | cut -f2,3 | \
	sort $SORT_OPTS -k1 | uniq -c | \
	sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
	sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.lemmas"
    
    cat $BUFFER | \
	sort $SORT_OPTS -k1 | uniq -c | \
	sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
	sort $SORT_OPTS -k4,4 -k3,3 -k2,2 | \
	awk '{print $1"\t"$4"\t"$3"\t"$2"\t"$5;}' > "$2.morphlex"
fi

rm -v $BUFFER
