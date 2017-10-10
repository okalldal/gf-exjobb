#!/bin/bash

TARBALL = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1989/Swedish-annotated-conll17.tar?sequence=41&isAllowed=y"

# Discover filenames
# curl -sL $TARBALL | tar -tv | head -n 20

FILENAME = 
# curl -sL $TARBALL | tar -xO $FILENAME | unxz | python conllu_parser.py | head -n 1000000 > tmp/buffer.tmp

# cat tmp/buffer.tmp | sort -k1 | uniq -c | awk '{print $1 "\t" $2"\t"$3}'