import re
import forms

def and_(*crit):
    return '(' + ' AND '.join(crit) + ')'
def or_(*crit):
    return '(' + ' OR '.join(crit)  + ')'

class Ticket:
    def __init__(self, rtclient):
        self.rt = rtclient
    def search(self, query=None,format='',orderby='id'):
        page = self.rt._do('search/ticket', query=query, format=format, orderby=orderby)
        if 'No matching results' in page:
            return []
        
        data = self.rt.split_res(page)

        if format=='i':
            return [x for x in data.split() if x]
        if format=='l':
            return forms.parse(data)

        if not format:
            ret = []
            for line in data.splitlines():
                if line:
                    ret.append(line.split(': ', 1))
            return ret
 
    def find_by_status(self, status=[], **kwargs):
        q = or_(*["status='%s'" % s for s in status])
        return self.search(query=q, **kwargs)

    def find_open(self, mapping={}, **kwargs):
        """Find any ticket whose status is new, open, or stalled"""
        q = or_(*["status='%s'" % s for s in ['new','open','stalled']])
        crit = [q]

        t = "'%s' = '%s'"
        for k, v in mapping.items():
            crit.append(t % (k,v))
        q = and_(*crit)
        print q
        return self.search(query=q, **kwargs)

    def find_by_cf(self, mapping, **kwargs):
        crit = []
        t = "'CF.{%s}' = '%s'"
        for k, v in mapping.items():
            crit.append(t % (k,v))

        q = " AND ".join(crit)
        return self.search(q, **kwargs)

    def find_by_ip(self, ip, **kwargs):
        return self.find_by_cf({'ip':ip}, **kwargs)


    def get(self, id):
        if 'ticket/' in id:
            id = int(id.replace('ticket/',''))
        self.id = id
        return self
    def show(self):
        page = self.rt._do('ticket/show', id=self.id)
        data = self.rt.split_res(page)
        return forms.parse(data)[0]
    def create(self, **fields):
        self.id = 'new'
        out = self.edit(**fields)
        match = re.search("200 Ok\n\n.*Ticket (\d+) created",out, re.MULTILINE)
        if match:
            id = match.groups()[0]
            self.id = id
            return self
        raise Exception("Error creating ticket %s" % out)

    def edit(self, **fields):
        fields['id'] = self.id
        content = forms.generate(fields)
        page = self.rt._do('ticket/edit', content=content)
        return page

    def attachment_ids(self):
        page = self.rt._do('ticket/%d/attachments' % self.id)
        data = self.rt.split_res(page)
        r =  forms.parse(data)
        if r:
            r = r[0]
            attachments = r['Attachments']
            return [int(x) for x in re.findall('(\d+):', attachments)]

    def get_attachment(self, attachment_id):
        page = self.rt._do('ticket/%d/attachments/%d' % (self.id, attachment_id))
        data = self.rt.split_res(page)
        r =  forms.parse(data)
        if r:
            return r[0]
__all__ = ["Ticket"]
