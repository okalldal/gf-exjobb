import sys
from signal import signal, SIGPIPE, SIG_DFL
import argparse
from collections import defaultdict
delimiter= '\t'

signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType('r'))
args = parser.parse_args()

counts=defaultdict(lambda: 0)
for line in args.file:
    l_split=line.strip('\n').split(delimiter)
    counts[l_split[1]]=float(l_split[0])
for line in sys.stdin:
    l_split=line.strip('\n').split(delimiter)
    fun=l_split[0]
    csum=sum([counts[lin] for lin in l_split[1:]])
    if csum != 0:
        linprobs=[(lin,counts[lin]/csum) for lin in l_split[1:]if counts[lin] !=0]
        print(*([fun]+list(sum(linprobs,()))),sep=delimiter)

