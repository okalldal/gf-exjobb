unigram_probs=$1
threshold=$2
grep "\.n\." $1 | python hyper_probs.py | python merge_synsets.py | cut -f 1,3
grep "\.v\." $1 | python hyper_probs.py | python merge_synsets.py | cut -f 1,3
