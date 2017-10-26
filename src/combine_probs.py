import argparse
PYTHONIOENCODING="UTF-8"


parser = argparse.ArgumentParser()
parser.add_argument('directory', type=str, help='Probability directory')
args = parser.parse_args()
directory = args.directory
total_count = 0
split_counts = list()
with open(directory+'total_splits.txt', mode='r',encoding='utf-8') as file:
    for l in file:
        l_split = l.strip('\n').split('\t')
        count = int(l_split[0])
        split = l_split[1]
        split_counts.append((split,count))
        total_count = total_count + count
for split, count in split_counts:
    with open(directory+split+'.txt', mode='r',encoding='utf-8') as file:
        for l in file:
            l_split = l.strip('\n').split('\t')
            prob = float(l_split[1])
            word = l_split[0]
            print(word, prob*count/total_count, sep='\t')