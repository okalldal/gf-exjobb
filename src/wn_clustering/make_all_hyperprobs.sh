grep "\.n\." wn_uni_autoparsed_th50_nodep.cnt| python hyper_probs.py > hyper_nouns.probs
grep "\.v\." wn_uni_autoparsed_th50_nodep.cnt| python hyper_probs.py > hyper_verbs.probs
grep "\.r\." wn_uni_autoparsed_th50_nodep.cnt| python hyper_probs.py > hyper_advs.probs
grep "\.[as]\." wn_uni_autoparsed_th50_nodep.cnt| python hyper_probs.py > hyper_adjs.probs
