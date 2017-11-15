from itertools import chain

def maxlen(strs):
    return max(map(len, map(str, strs)))

def show(title, pairs):
    keys, vals = zip(*pairs)
    maxkey, maxval = maxlen(keys), maxlen(vals)
    lines = [
        '| {key:<{keypad}}: {val:<{valpad}} |'.format(
            keypad=maxkey, valpad=maxval, key=key, val=val)
        for key, val in pairs
    ]
    longest = maxlen(lines)
    if longest < len(title):
        lines = [line[:-1] + (len(title)-len(line)) * ' ' + '    |' for line in lines]
        footer = '+' + ('-' * (len(title)+2)) + '+'
    else:
        footer = '+' + ('-' * (longest-2)) + '+'
    header = '+{:-^{length}}+'.format(' %s ' % title, length=longest-2)
    return '\n'.join(chain([header], lines, [footer]))
