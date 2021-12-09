import os

symbols = set()
models = list(filter(lambda x: x.endswith('.model'), os.listdir(os.getcwd())))
for i in models:
    with open(i) as file:
        for j in ''.join(file.read().split('\n')):
            symbols.add(j)

replace = dict((i, input('Enter symbol to replace "%s": ' % i)[0]) for i in symbols)

for i in models:
    raw = open(i).read()
    for j in replace:
        raw = raw.replace(j, replace[j])
    with open(i, 'w') as file:
        file.write(raw)
