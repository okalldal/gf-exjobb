import sys
from os.path import basename, splitext

delim = ', '
f = lambda x: '{0:.1f}%'.format(x)

print(delim.join(['File', 'Model', 'Precision', 'Recall', 'F1']))
for filename in sys.argv[1:]:
    fobj = open(filename)
    name = splitext(basename(filename))[0]

    random_p = []
    random_r = []

    while True:
        model = fobj.readline()
        data = fobj.readline()

        if not model or not data:
            break

        data = data.strip().split(' ')
        total = float(data[1][:-1])
        no_error = float(data[4][:-1])
        correct = float(data[7][:-1])
        random =  float(data[13][:-1])
        random_p.append(random/no_error*100)
        random_r.append(random/total*100)
        P = correct/no_error*100
        R = correct/total*100
        F1 = 2*P*R/(P+R)

        print(', '.join([name, model.strip(), f(P), f(R), f(F1)]))

    P = sum(random_p)/len(random_p)
    R = sum(random_r)/len(random_r)
    F1 = 2*P*R/(P+R)
    print(delim.join([name, 'random', f(P), f(R), f(F1)]))

    fobj.close()
