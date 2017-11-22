import sys
from nltk.corpus import wordnet as wn
from signal import signal, SIGPIPE, SIG_DFL
import argparse

delimiter= '\t'

signal(SIGPIPE, SIG_DFL)

parser = argparse.ArgumentParser()
parser.add_argument('-c', type=float, default=1e-5)
args = parser.parse_args()

ssprobs=dict()
for line in sys.stdin:
    l_split=line.strip('\n').split(delimiter)
    prob=float(l_split[0])
    ss=wn.synset(l_split[1])
    if prob>args.c:
        ssprobs[ss.offset()]=prob
    ss_stack=[ss]
    final_ss=set()
    while len(ss_stack)>0:
        current_ss=ss_stack.pop()
        if current_ss.offset() in ssprobs.keys():
            final_ss.add(current_ss)
        for hn in current_ss.hypernyms():
            ss_stack.append(hn)
    if len(final_ss)>0:
        output=[(ssprobs[hn.offset()],hn.name()) for hn in final_ss]
        output.sort()
        output=list(sum(output,()))
        print(*([prob,ss.name()]+output),sep=delimiter)
'''
    else:
        new_ss=ss
        new_prob=prob
        while new_prob<args.c:
            if new_ss.hypernyms()==[]:
                print('No hypernyms',ss.name(),new_ss.name(),file=sys.stderr)
                break
            elif args.o:
                chosen_ss=new_ss.hypernyms()[0]
                chosen_prob=ssprobs[chosen_ss.offset()] if chosen_ss.offset() in ssprobs.keys() else new_prob
                for hn in new_ss.hypernyms():
                    hn_prob=ssprobs[hn.offset()] if hn.offset() in ssprobs.keys() else new_prob
                    if hn_prob<chosen_prob:
                        chosen_ss = hn
                        chosen_prob=ssprobs[chosen_ss.offset()] if chosen_ss.offset() in ssprobs.keys() else new_prob
                new_ss=chosen_ss
                new_prob=chosen_prob
            else:
                new_ss=new_ss.hypernyms()[0]
                if new_ss.offset() in ssprobs.keys():
                    new_prob=ssprobs[new_ss.offset()]
    print(prob, ss.name(),new_prob,new_ss.name(),sep=delimiter)
'''
