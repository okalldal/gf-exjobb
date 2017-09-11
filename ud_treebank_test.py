import nltk
from collections import Counter

UD_PATH = "ud-data/UD_English-r1.3/en-ud-dev.conllu"

lines = []
with open(UD_PATH) as f:
    current = []
    for line in f:
        if line == "\n":
            lines.append(current)
            current = []
        current.append(line)
lines = map(''.join, lines)


head_lists = dict()
for conllu_string in lines:
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
