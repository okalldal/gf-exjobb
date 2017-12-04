unigram_probs=$1
threshold=$2
grep "\.n\." $1 | python hyper_probs.py | python merge_synsets.py | cut -f 2,4
grep "\.v\." $1 | python hyper_probs.py | python merge_synsets.py | cut -f 4,4
