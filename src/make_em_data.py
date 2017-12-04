from itertools import product
import sys
import argparse
PYTHONIOENCODING="UTF-8"



parser = argparse.ArgumentParser(description='''
This script generates data files to be fed to wn_em.py or new_em.py from a possibility dictionary and count files in tsv format.
 Specify which columns are feature columns with the f flag. In an n-gram model, each lexical item is separated with : and
 each feature within these lexical items separated by ,. The data is written to separate files based on the columns given 
  in the s flag, for example if one wants to process words with different pos tags or deprel tags separately.
  Example: A bigram model on the form: count <tab> lemma1 <tab> pos1 <tab> deprel <tab> lemma2 <tab> pos2, with both 
  lexical items having their possibility info taken from the possibility dictionary dict.tsv and one wants to split the 
  data into separate files according to deprel the script can be run with:
  python make_em_data -c 0 -s 3 -f 1:2,4:5 -p dict.tsv dict.tsv" 
  Please refer to make_all_em_data.sh for further examples of usage.
''')
parser.add_argument('-l', type=int, help='Number of fields of proper rows, rows with fewer columns will be filled with root symbols.', default=0)
parser.add_argument('-r', type=str, help='Root symbol', default='ROOT')
parser.add_argument('-m', type=str, help='Out of vocabulary items will be given this value in first feature column,other feature columns are carried', default=None)
parser.add_argument('-c', type=int, help='Count column, one column, -1 chooses last column automatically', required=True)
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
if count_column == -1 and args.l != 0:
    print('Using -l >0 with -c = -1 is not supported.', file=sys.stderr)
    quit(1)

for file, cols in zip(args.p, feature_columns):
    possibilities = dict()
    for l in file:
        l_split = l.strip('\n').split('\t')
        word = tuple(l_split[:len(cols)])
        funs = l_split[len(cols):]
        if word in possibilities.keys():
            possibilities[word]=list(set(possibilities[word]+funs))
        else:
            possibilities[word] = funs
    poss_dicts.append(possibilities)
file_pool=dict()
split_counts = dict()
for l in sys.stdin:
    l_split = l.strip('\n').split('\t')

    if len(l_split) < row_length and row_length>0:
        l_split = l_split + [args.r]*(row_length-len(l_split))
    count = int(l_split[count_column])
    multigram_possibilities = []
    multigram_features = []
    skip = False
    for pd, f_cols in zip(poss_dicts, feature_columns):
        feature = tuple([l_split[col] for col in f_cols])

        if feature in pd.keys():
            #Feature in vocabulary
            possibilities = pd[feature]
        elif any([l_split[col] == 'ROOT' for col in f_cols]):
            #Root
            possibilities = [args.r]
        elif args.m is not None:
            #OOV This is not a good idea as it needs a recount
            possibilities = '_'.join([args.m]+[l_split[col] for col in f_cols[1:]])
        else:
            #OOV and skip OOV
            skip = True
            break
        multigram_features.append(feature)
        multigram_possibilities.append(possibilities)
    if skip is True:
        #print(l_split, file=sys.stderr)
        continue

    multigram_possibilities = [unigram for ngram in product(*multigram_possibilities) for unigram in ngram]
    multigram_features = [f_col for feature in multigram_features for f_col in feature]
    split_id = tuple([l_split[col] for col in splitcols])

    if split_id not in file_pool.keys():
        file_name = '_'.join(split_id) + '.txt'
        file = open(outpath + '/' + file_name, mode='w+', encoding='utf-8')
        print('---', file=file)
        file_pool[split_id] = file
        split_counts[split_id] = 0
    split_counts[split_id] = split_counts[split_id] + count
    print(*([count]+multigram_features+multigram_possibilities), sep='\t', file=file_pool[split_id])

for file in file_pool.values():
    file.close()
with open(outpath + '/' + '1_splits.txt', mode='w+', encoding='utf-8') as f:
    for split, count in split_counts.items():
        print(count,'_'.join(split), sep='\t', file=f)
