import sys

for line in sys.stdin:
    l_split=line.strip('\n').split('\t')
    print(*(l_split[:2]+sorted(set(l_split[2:]))),sep='\t')
