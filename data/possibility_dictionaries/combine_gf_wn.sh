#!/usr/bin/env bash
for file in $(comm -12 <(ls gf) <(ls wn2))
do
    cat wn/$file <(awk -v FS='\t' -v OFS='\t' '$2 !~ /NOUN|VERB|ADJ|ADV|PROPN/' gf/$file) |sort -k2,2 -k1,1> gf_wn/$file
done
