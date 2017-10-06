import edward as ed 
import tensorflow as tf
from edward.models import Dirichlet, Categorical, Multinomial
from collections import Counter

langs = ['English', 'Swedish']

corpus = [
    ['bank', 'bank', 'bank'],               # English
    ['flodkant', 'bank', 'bank']    # Swedish
]

vocabulary = [
    ['bank'],
    ['bank', 'flodkant']
]

synsets = ['bank.n.1', 'bank.n.2']

L = [
    {'bank.n.1': 'bank', 'bank.n.2': 'bank'},
    {'bank.n.1': 'bank', 'bank.n.2': 'flodkant'}
]

L2 = [
    [[1.0, 1.0]],
    [[1.0, 0.0], [0.0, 1.0]]
]

num_lang = len(vocabulary)
one_hot = lambda indices, n: [1 if i in indices else 0 for i in range(n)]

vocab_to_id = [{vocabulary[lang][i]: i for i in range(len(vocabulary[lang]))} for lang in range(len(vocabulary))]
id_corpus = [[vocab_to_id[lang][w] for w in corpus[lang]] for lang in range(len(corpus))]
synset_to_id = {synsets[i]: i for i in range(len(synsets))}
id_L = [[vocab_to_id[lang][L[lang][s]] for s in synsets] for lang in range(len(L))]
counters = [Counter(corpus[lang]) for lang in range(num_lang)]
counts = [[(vocab_to_id[lang][word], c) for word, c in counters[lang].items()] for lang in range(num_lang)]
counts = [[float(count) for index, count in sorted(counts[lang], key=lambda t: t[0])] for lang in range(num_lang)]

#print(counts)

abstr = Dirichlet(concentration=(tf.ones(len(L2))), name="Abstract")
concrete = [tf.einsum('n,mn->m', abstr, tf.constant(L2[lang])) for lang in range(len(L2))]

words = [Multinomial(probs=concrete[lang], name=langs[lang], total_count=float(sum(counts[lang]))) for lang in range(num_lang)]


# variational distribution
qabstr = Dirichlet(concentration=tf.Variable(tf.ones([len(synsets)])), validate_args=True)

data = {words[lang]: tf.constant(counts[lang]) for lang in range(num_lang)}
latent_vars = {abstr: qabstr}
inference = ed.KLqp(latent_vars=latent_vars, data=data)

inference.run(logdir='log')
sess = ed.get_session()

print(sess.run(qabstr.mean()))
