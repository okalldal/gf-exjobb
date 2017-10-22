from signal import signal, SIGPIPE, SIG_DFL
import argparse
import sys

#Count should always be on first column

delimiter= '\t'
#count_col=0

signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', type=argparse.FileType(mode='r', encoding='utf-8'), default=sys.stdin)
parser.add_argument('outfile', nargs='?', type=argparse.FileType(mode='w', encoding='utf-8'), default=sys.stdout)
args = parser.parse_args()

counts = dict()
current = None
current_count = 0
for l in args.infile:
    l_split = l.strip('\n').split(delimiter)
    count = int(l_split[0])
    feature = tuple(l_split[1:])
    if feature != current:
        if current is not None:
            print(*([current_count]+list(current)),sep=delimiter, file=args.outfile)
        current = feature
        current_count = count
    else:
        current_count = current_count + count
print(*([current_count]+list(current)), sep=delimiter, file=args.outfile)
