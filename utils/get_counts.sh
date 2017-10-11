#!/bin/bash

TARBALL="https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1989/Swedish-annotated-conll17.tar?sequence=41&isAllowed=y"
LANGUAGE='swe'
#SORT_OPTS="-S 50% --parallel=8 -T $PWD/tmp";
SORT_OPTS="-S 50% -T $PWD/tmp"
MAX_LINES=1000000


mkdir -p $PWD/tmp

# Discover filenames
# curl -sL $TARBALL | tar -tv | head -n 20

# Download the top NUM conllu-lines and save to a temp file
BUFFER=tmp/buffer-$LANGUAGE.tmp
curl -sL $TARBALL | tar -xO | unxz | python conllu_parser.py | head -n $MAX_LINES > $BUFFER
echo "Downloaded UD sentences, starting to count"
# read the file and do the counts
cat $BUFFER | cut -f1,5 | sort $SORT_OPTS -k1 | uniq -c | awk '{print $1 "\t" $2"\t"$3}' > $LANGUAGE.counts
rm $BUFFER 
echo "Wrote file $LANGUAGE.counts"