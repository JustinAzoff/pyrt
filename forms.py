import re
whitespace = re.compile("(\s+)")
def parse(lines):
    state = 0
    comments = []
    l = 0
    hash = {}
    while l < len(lines):
        line = lines[l]
        if not line:
            l+=1
            continue
        
        if state == 0 and line[0]=='#':
            while l < len(lines) and line[0]=='#':
                comments.append(line)
                l+=1
            state = 1

        field, value = line.split(":", 1)
        if value.startswith(" "): value=value[1:]
        values = []
        while l+1 < len(lines) and lines[l+1].startswith(" "):
            values.append(lines[l+1])
            l+=1
        # Strip longest common leading indent from text.
        min=1000
        for v in values:
            g = whitespace.match(v)
            if g:
                n = len(g.groups()[0])
                if n < min: min=n
        values = [v[min:] for v in values]
        values.insert(0, value)
        value = '\n'.join(values)
        hash[field] = value 
        l+=1
    hash['comments'] = comments
    return hash

def generate(fields):
    lines = []
    for k,v in fields.items():
        v = str(v)
        if k == 'cf': continue
        if '\n' not in v:
            lines.append("%s: %s" % (k,v))
        else:
            stuff = v.splitlines()
            lines.append("%s: %s" % (k,stuff[0]))
            for s in stuff[1:]:
                lines.append("   %s" % s)

    if 'cf' in fields:
        for k, v in fields['cf'].items():
            lines.append("CF-%s: %s" % (k,v))

    lines.append('')
    return '\n'.join(lines)
