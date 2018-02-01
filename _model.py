from pprint import pprint
import os

next_model = {"u": "r", "r": "d", "d": "l", "l": "u", "c": "c"}
# next_model = {"u": "l", "d": "r", "r": "u", "l": "d", "c": "c"}
os.chdir('data/models/')


def rename(s):
    r = ''
    for i in s.split('_')[0]:
        r += next_model[i]
    r = ''.join(sorted(r))
    r += '_'+s.split('_')[1]
    return r


for i in os.listdir(os.getcwd()):
    name = i
    print(i)
    model = [[int(j) for j in i] for i in open(i).read().split('\n')]
    pprint(model)
    for _ in range(3):
        model = list(zip(*model[::-1]))
        name = rename(name)
        open(name, 'w').write('\n'.join(''.join(str(j) for j in i) for i in model))
