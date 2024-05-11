from itertools import groupby

data = [1, 2, 3, 13, 5, 6, 7, 8, 9, 11, 25, 26, 27]

result = []

for k, g in groupby(enumerate(data), lambda x: x[0]-x[1]):
    items = [i[1] for i in g]
    if len(items) > 1:
        result.append('{}...{}'.format(items[0], items[-1]))
    else:
        result.append(str(items[0]))

print(', '.join(result))  # 1...9, 11, 25...27