import nltk
from collections import Counter

conllu_strings = ['''1	President	President	PROPN	NNP	Number=Sing	5	nsubj	_	_
2	Bush	Bush	PROPN	NNP	Number=Sing	1	flat	_	_
3	on	on	ADP	IN	_	4	case	_	_
4	Tuesday	Tuesday	PROPN	NNP	Number=Sing	5	obl	_	_
5	nominated	nominate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
6	two	two	NUM	CD	NumType=Card	7	nummod	_	_
7	individuals	individual	NOUN	NNS	Number=Plur	5	obj	_	_
8	to	to	PART	TO	_	9	mark	_	_
9	replace	replace	VERB	VB	VerbForm=Inf	5	advcl	_	_
10	retiring	retire	VERB	VBG	VerbForm=Ger	11	amod	_	_
11	jurists	jurist	NOUN	NNS	Number=Plur	9	obj	_	_
12	on	on	ADP	IN	_	14	case	_	_
13	federal	federal	ADJ	JJ	Degree=Pos	14	amod	_	_
14	courts	court	NOUN	NNS	Number=Plur	11	nmod	_	_
15	in	in	ADP	IN	_	18	case	_	_
16	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
17	Washington	Washington	PROPN	NNP	Number=Sing	18	compound	_	_
18	area	area	NOUN	NN	Number=Sing	14	nmod	_	SpaceAfter=No
19	.	.	PUNCT	.	_	5	punct	_	_''',\
'''1	Bush	Bush	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	also	also	ADV	RB	_	3	advmod	_	_
3	nominated	nominate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
4	A.	A.	PROPN	NNP	Number=Sing	3	obj	_	_
5	Noel	Noel	PROPN	NNP	Number=Sing	4	flat	_	_
6	Anketell	Anketell	PROPN	NNP	Number=Sing	4	flat	_	_
7	Kramer	Kramer	PROPN	NNP	Number=Sing	4	flat	_	_
8	for	for	ADP	IN	_	13	case	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	13	det	_	_
10	15	15	NUM	CD	NumType=Card	12	nummod	_	SpaceAfter=No
11	-	-	PUNCT	HYPH	_	12	punct	_	SpaceAfter=No
12	year	year	NOUN	NN	Number=Sing	13	compound	_	_
13	term	term	NOUN	NN	Number=Sing	3	obl	_	_
14	as	as	ADP	IN	_	16	case	_	_
15	associate	associate	ADJ	JJ	Degree=Pos	16	amod	_	_
16	judge	judge	NOUN	NN	Number=Sing	13	nmod	_	_
17	of	of	ADP	IN	_	19	case	_	_
18	the	the	DET	DT	Definite=Def|PronType=Art	19	det	_	_
19	District	District	PROPN	NNP	Number=Sing	16	nmod	_	_
20	of	of	ADP	IN	_	22	case	_	_
21	Columbia	Columbia	PROPN	NNP	Number=Sing	22	compound	_	_
22	Court	Court	PROPN	NNP	Number=Sing	19	nmod	_	_
23	of	of	ADP	IN	_	24	case	_	_
24	Appeals	Appeals	PROPN	NNPS	Number=Plur	22	nmod	_	SpaceAfter=No
25	,	,	PUNCT	,	_	3	punct	_	_
26	replacing	replace	VERB	VBG	VerbForm=Ger	3	advcl	_	_
27	John	John	PROPN	NNP	Number=Sing	26	obj	_	_
28	Montague	Montague	PROPN	NNP	Number=Sing	27	flat	_	_
29	Steadman	Steadman	PROPN	NNP	Number=Sing	27	flat	_	SpaceAfter=No
30	.	.	PUNCT	.	_	3	punct	_	_''']

head_lists = dict()
for conllu_string in conllu_strings:
    dg = nltk.parse.DependencyGraph(
        tree_str = conllu_string, top_relation_label='root')

    for head, rel, dep in dg.triples():
        if not dep in head_lists.keys():
            head_lists[dep] = []
        head_lists[dep].append((rel, head))

head_counters = dict()
for lemma in head_lists.keys():
    head_list = head_lists[lemma]
    head_counter = Counter(head_list)
    head_counters[lemma] = head_counter
    print("----------")
    print(lemma, len(head_list))
    print(head_counter.most_common(10))
