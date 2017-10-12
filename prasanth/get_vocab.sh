#!/bin/bash

TMP="$PWD/tmp"   # temporary directory for gnu sort and intermediate outputs
if [[ ! -d "${TMP}" ]] ; then
  mkdir -p "${TMP}";
fi

TAB=`echo -e "\t"`
#SORT_OPTS="-S 50% --parallel=8 -T $PWD/tmp";
SORT_OPTS="-S 50% -T $PWD/tmp"
export LC_ALL=C

FRDR=""             # reader program for input file
#https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html#Shell-Parameter-Expansion
fileext="${1##*.}"  # get extension of input file
if [[ "$fileext" == "bz2" ]] ; then
  FRDR="bzcat";
elif [[ "$fileext" == "gz" ]] ; then
  FRDR="gzcat";
else
  FRDR="cat";
fi

PREPROC_LC=false   #true    # lower-cased or not 
MORPH_TAGGED=true           # extract morph-feats or not

if [ $PREPROC_LC = true ] ; then
  transformer='{printf("%s\t%s\t",tolower($1),tolower($2));for(i=3;i<NF;i++){printf("%s\t",$i);}printf("%s\n",$i)}'
else
  transformer='{printf("%s\t%s\t",$1,$2);for(i=3;i<NF;i++){printf("%s\t",$i);}printf("%s\n",$i)}'
fi

if [ $MORPH_TAGGED = true ] ; then
  FIELDS="-f2,3,4,6"
else
  FIELDS="-f2,4"
fi

BUFFER="$TMP/$$.buffer"
eval $FRDR $1 | grep -v -e "^#" -e "^$" | \
  cut "$FIELDS" | \
  awk "$transformer" \
  > $BUFFER

# lower-cased surface forms
cat $BUFFER | \
  awk -F"$TAB" '{print $1"\t"$3;}' | \
  sort $SORT_OPTS -k1 | uniq -c | \
  sed -e 's/^[ \t]*//g' -e $'s/ /\t/g' | \
  sort $SORT_OPTS -k1,1nr --stable -t"$TAB" > "$2.vcb"

cat "$2.vcb" | \
  sort $SORT_OPTS -k2,3 --stable -t"$TAB" | \
  awk -F"$TAB" '{ 
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
