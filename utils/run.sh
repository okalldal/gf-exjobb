#!/bin/bash

# Discover filenames
curl -sL "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1989/Swedish-annotated-conll17.tar?sequence=41&isAllowed=y" | tar -tv | head -n 20

read -n 1 -p "Input filename: " filename

curl -sL "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1989/Swedish-annotated-conll17.tar?sequence=41&isAllowed=y" | tar -xO $filename | unxz | head -n 100 | awk '{print $0}' RS=