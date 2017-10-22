from itertools import product
import sys
import argparse
PYTHONIOENCODING="UTF-8"


parser = argparse.ArgumentParser()
parser.add_argument('-l', type=int, help='Number of fields of proper rows, rows with other number of fields are ignored', default=0)
parser.add_argument('-c', type=int, help='Count column, one column', required=True)
parser.add_argument('-s', type=str, help='Split columns, comma separated', default='')
parser.add_argument('-f', type=str, help='Feature columns, features comma separated, columns : separated', required=True)
parser.add_argument('-o', type=str, help='Output directory', required=True)
parser.add_argument('-i', type=str, help='Identity columns, will be carried without dictionary')
parser.add_argument('-p', type=argparse.FileType(mode='r', encoding='utf-8'), nargs='+', help='List of possibility dicts, one for each feature', required=True)
args = parser.parse_args()
poss_dicts = list()
splitcols = [int(col) for col in args.s.split(',')]
feature_columns = [[int(col) for col in feature.split(':')] for feature in args.f.split(',')]
count_column = args.c
outpath = args.o
row_length = args.l
for file, cols in zip(args.p, feature_columns):
    possibilities = dict()
    for l in file:
        l_split = l.strip('\n').split('\t')
        word = tuple(l_split[:len(cols)])
        funs = l_split[len(cols):]
        possibilities[word] = funs
    poss_dicts.append(possibilities)
file_pool=dict()
split_counts = dict()
for l in sys.stdin:
    l_split = l.strip('\n').split('\t')
    len_l = len(l_split)
    if len_l != row_length:
        continue #TODO root handling
    count = int(l_split[count_column])
    split_id = tuple([l_split[col] for col in splitcols])
    multigram_features = [tuple([l_split[col]for col in f_cols]) for f_cols in feature_columns]
    if all([feature in pd.keys() for feature, pd in zip(multigram_features,poss_dicts)]):
        if split_id not in file_pool.keys():
            file_name = '_'.join(split_id) + '.txt'
            file = open(outpath + '/' + file_name, mode='w+', encoding='utf-8')
            print('---', file=file)
            file_pool[split_id] = file
            split_counts[split_id] = 0
        split_counts[split_id] = split_counts[split_id] + count
        multigram_possibilities = product(*[pd[tuple([l_split[col]for col in f_cols])] for pd, f_cols in zip(poss_dicts, feature_columns)])
        print(*([count, multigram_features]+list(multigram_possibilities)), sep='\t', file=file_pool[split_id])
    else:
        pass#TODO OOV handling
for file in file_pool.values():
    file.close()
with open(outpath + '/' + 'splits.txt', mode='w+', encoding='utf-8') as f:
    for split, count in split_counts.items():
        print(count,'_'.join(split), sep='\t', file=f)
