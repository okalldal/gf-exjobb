import sys

while True:
    name = sys.stdin.readline()
    data = sys.stdin.readline()

    if not name or not data:
        break

    data = data.strip().split(' ')
    total = float(data[1][:-1])
    no_error = float(data[4][:-1])
    #correct = float(data[7][:-1])
    correct = float(data[10][:-1])
    P = correct/no_error*100
    R = correct/total*100
    F1 = 2*P*R/(P+R)

    print(name.strip())
    print('P=%.1f' % P)
    print('R=%.1f' % R)
    print('F1=%.1f' % F1)
