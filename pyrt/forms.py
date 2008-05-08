# pyrt/forms.py
# Copyright (C) 2007, 2008 Justin Azoff JAzoff@uamail.albany.edu
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

"""This module is for parsing the
custom key=>value format that RT uses with
its REST interface
"""

import re

from odict import OrderedDict

whitespace = re.compile("(\s+)")
def parse_one_form(data):
    lines = data.split('\n')
    state = 0
    comments = []
    l = 0
    hash = OrderedDict()
    while l < len(lines):
        line = lines[l]
        if not line:
            l+=1
            continue
        
        if state == 0 and line[0]=='#':
            while l < len(lines) and line and line[0]=='#':
                line = lines[l]
                comments.append(line[2:])
                l+=1
            state = 1
        if ':' not in line:
            l+=1
            continue

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
        if value=='': value=None
        if value=='Not set': value=None
        hash[field] = value 
        l+=1
    if comments:
        hash['rt_comments'] = comments
    if 'id' in hash:
        hash['id'] = hash['id'].replace('ticket/','')
    return hash

def parse(data):
    if '\n--\n\n' in data:
        forms = data.split("\n--\n\n")
        return [parse_one_form(f) for f in forms]
    else:
        return [parse_one_form(data)]

def generate(fields):
    lines = []
    for k,v in fields.items():
        if k == 'cf': continue
        if '\n' not in str(v):
            if v is None: v=''
            lines.append("%s: %s" % (k,v))
        else:
            stuff = v.split('\n')
            lines.append("%s: %s" % (k,stuff[0]))
            for s in stuff[1:]:
                lines.append("   %s" % s)

    if 'cf' in fields:
        for k, v in fields['cf'].items():
            if v is None: v=''
            lines.append("CF-%s: %s" % (k,v))

    lines.append('')
    return '\n'.join(lines)
