import pgf
import sys

print('reading pgf')
gr = pgf.readPGF('../data/TranslateEngSwe.pgf')
eng = gr.languages['TranslateEng']
swe = gr.languages['TranslateSwe']
# ita = gr.languages['TranslateIta']

for sent in sys.stdin:
    print('===========================')
    count = 0
    for p, ex in eng.parse(sent.strip()):
        count += 1
        if count > 10:
            break
        print(p)
        print(ex)
        print(eng.linearize(ex))
        print(swe.linearize(ex))