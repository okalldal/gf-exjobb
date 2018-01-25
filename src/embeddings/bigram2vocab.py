from sys import stdin
from collections import Counter
root_count = 0
dep_counts = Counter()
for l in stdin:
    l_split = l.strip('\n').split()
    if l_split[2]=='ROOT':
        root_count = root_count+int(l_split[0])
    dep_counts[l_split[1]]+=int(l_split[0])
print('ROOT',root_count,sep=' ')
for item, count in dep_counts.most_common():
    print(item,count,sep=' ')
