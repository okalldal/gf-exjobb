import argparse
import gzip
PYTHONIOENCODING="UTF-8"


parser = argparse.ArgumentParser()
parser.add_argument('-s', type=str, default="", help='keep splits, separated by comma')
parser.add_argument('-p', type=str, default='./', help='Probability directory')
parser.add_argument('-o', type=str, default='./', help='Out directory')
args = parser.parse_args()
in_directory = args.p
out_directory = args.o
total_count = 0
#if parser.s == "":
#    keep_splits = None
#else
keep_splits = [int(i) for i in args.s.split(',')]
split_counts = list()

with open(in_directory+'1_splits.txt', mode='r',encoding='utf-8') as file:
    for l in file:
        l_split = l.strip('\n').split('\t')
        count = int(l_split[0])
        split = l_split[1]
        split_counts.append((split,count))
        total_count = total_count + count
for split, count in split_counts:
    with open(in_directory+split+'.probs', mode='r',encoding='utf-8') as file:
        if keep_splits == []:
            name = 'all'
        else:
            split_cols = split.split('_')
            name = '_'.join([split_cols[i] for i in keep_splits])
        with open(out_directory+name+'.probs', mode='a+') as out_file:
            for l in file:
                l_split = l.strip('\n').split('\t')
                prob = float(l_split[0])
                word = l_split[1:]
                print(*([prob*count/total_count] + word), sep='\t', file=out_file)