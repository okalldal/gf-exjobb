import sys
from signal import signal, SIGPIPE, SIG_DFL
import argparse
from collections import defaultdict

delimiter= '\t'

signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=int, default=1)
args = parser.parse_args()

fun2linearizations=defaultdict(list)
for line in sys.stdin:
    l_split=line.strip('\n').split(delimiter)
    for fun in l_split[args.f:]:
        fun2linearizations[fun].append(tuple(l_split[:args.f]))
for fun, lins in fun2linearizations.items():
    print(*([fun]+list(sum(lins,()))),sep=delimiter)
