import pgf
import re

def get_terminals(exp):
    fun, argx = exp.unpack()
    if len(argx) == 0:
        return [fun]
    else:
        out = []
        for a in argx:
            out.extend(get_terminals(a))
        return out

def get_type(gr, fun):
    try:
        return gr.functionType(fun).cat
    except KeyError:
        return None

if __name__ == "__main__": 
    gr = pgf.readPGF('../data/translate-pgfs/TranslateEng.pgf')
    eng = gr.languages['TranslateEng']

    lin = lambda fun: eng.linearize(pgf.readExpr(fun))

    with open('../data/treebanks/rgl-api-trees.txt') as f:
        trees = [l.strip() for l in f]

    alts = []
    for tree in trees:
        exp = pgf.readExpr(tree)
        terms = get_terminals(exp)
        lins = [eng.linearize(pgf.readExpr(w)) for w in terms]
        alts.append({
            s: {
                x for x,_,_ in eng.lookupMorpho(l) 
                if get_type(gr, x) == get_type(gr, s)
                if lin(x) == lin(s)
            }
            for s,l in zip(terms,lins)
            if l != ''
            if not re.match('^\[.*\]$', l)
        })

def over2(g):
    fs = len(g.items())
    tot = sum([len(alts) for f, alts in g.items()])
    return fs < tot

def sense(g):
    for fun, alts in g.items():
        if any(any(char.isdigit() for char in word) for word in alts):
            return True
    return False