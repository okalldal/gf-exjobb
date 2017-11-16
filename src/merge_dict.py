from signal import signal, SIGPIPE, SIG_DFL
import argparse
import sys

#Count should always be on first column

delimiter= '\t'
#count_col=0

signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser()
args = parser.parse_args()

current = None
current_funs = []
for l in sys.stdin:
    l_split = l.strip('\n').split(delimiter)
    fun = l_split[-1]
    word = tuple(l_split[:-1])
    if word != current:
        if current is not None:
            print(*(list(current) + current_funs), sep=delimiter)
        current = word 
        current_funs = [fun]
    else:
        current_funs.append(fun)
#Print the last value
print(*(list(current) + current_funs), sep=delimiter)
