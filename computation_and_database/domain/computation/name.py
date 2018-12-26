import numpy as np
letters_to_contain = set(['i', 'o', 'n', 'p', 'm'])
names = np.genfromtxt('yob2016.txt', dtype=str, delimiter=',')[:,0]
print(names.shape)
result = list()
for name in names:
    name = name.lower()
    c = 0
    for letter in letters_to_contain:
        if letter not in name:
            c += 1
    if c<2:
        result.append(name)
result.sort(key = lambda s: len(s))
for r in result:
    print(r)