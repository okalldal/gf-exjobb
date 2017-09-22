from collections import defaultdict
LABEL_STRING = '''N       NOUN
PN      PROPN
A       ADJ
AdA     ADJ
V       VERB 
V2      VERB 
V3      VERB
VV      VERB
VA      VERB 
VV      AUX
VS      VERB 
VQ      VERB
V2V     VERB
V2A     VERB
V2S     VERB
V2Q     VERB
AdA     ADV
AdN     ADV
AdV     ADV
Adv     ADV
IAdv    ADV
Conj    CONJ
Pron    PRON
NP      PRON
Det     PRON
IP      PRON
Predet  DET
Det     DET
IDet    DET
Quant   DET
IQuant  DET
Interj  INTJ
Prep    ADP
Subj    SCONJ
Subj    ADV'''
#Handle NUM SYM PUNCT
ud2gf_cats = defaultdict(list)
for line in LABEL_STRING.splitlines():
    gf, ud = line.split()
    ud2gf_cats[ud].append(gf)
print(ud2gf_cats)
{'NOUN': ['N'],
 'PROPN': ['PN'],
 'ADJ': ['A', 'AdA'],
 'VERB': ['V', 'V2', 'V3', 'VV', 'VA', 'VS', 'VQ', 'V2V', 'V2A', 'V2S', 'V2Q'],
 'AUX': ['VV'],
 'ADV': ['AdA', 'AdN', 'AdV', 'Adv', 'IAdv', 'Subj'],
 'CONJ': ['Conj'],
 'PRON': ['Pron', 'NP', 'Det', 'IP'],
 'DET': ['Predet', 'Det', 'IDet', 'Quant', 'IQuant'],
 'INTJ': ['Interj'],
 'ADP': ['Prep'],
 'SCONJ': ['Subj']}
