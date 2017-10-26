from signal import signal, SIGPIPE, SIG_DFL
import argparse
import sys

#Count should always be on first column

delimiter= '\t'
#count_col=0

signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser()
parser.add_argument('-f', action='store_true')
parser.add_argument('-c', action='store_true')
args = parser.parse_args()

counts = dict()
current = None
current_count = 0
for l in sys.stdin:
    l_split = l.strip('\n').split(delimiter)
    if not args.c:
        count = l_split[0]
        feature = tuple(l_split[1:])
    else:
        count = l_split[-1]
        feature = tuple(l_split[:-1])
    if args.f:
        count = float(count)
    else:
        count = int(count)
    if feature != current:
        if current is not None:
            print(*([current_count]+list(current)), sep=delimiter)
        current = feature
        current_count = count
    else:
        current_count = current_count + count
#Print the last value
print(*([current_count]+list(current)), sep=delimiter)
