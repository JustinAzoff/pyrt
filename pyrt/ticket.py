import re
import forms

def and_(crit):
    return '(' + ' AND '.join(crit) + ')'
def or_(crit):
    return '(' + ' OR '.join(crit)  + ')'

class Field:
    def __init__(self, name):
        self.name=name

    def __eq__(self, other):
        return self._compare(self.name, other, '=')
    def __ne__(self, other):
        return self._compare(self.name, other, '!=')
    def __gt__(self, other):
        return self._compare(self.name, other, '>')
    def __lt__(self, other):
        return self._compare(self.name, other, '<')

    def like(self, other):
        return self._compare(self.name, other, 'LIKE')
    contains = like


    def _compare(self, name, other, op):
        t = "'%s' %s '%s'"
        return t % (name, op, other)

class FieldWrapper:
    def __init__(self, custom=False):
        self.custom=custom
        self.cf = None
    def __getattr__(self, attr):
        if self.custom:
            return Field('CF.{%s}' % attr)
        else:
            return Field(attr)

class Ticket:
    def __init__(self, rtclient):
        self.rt = rtclient
        self.c = FieldWrapper()
        self.c.cf = FieldWrapper(custom=True)

    def search(self, query=None,format='',orderby='id'):
        print query
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
        q = or_([self.c.status==s for s in status])
        return self.search(query=q, **kwargs)

    def find_open(self, query=[], **kwargs):
        """Find any ticket whose status is new, open, or stalled"""
        q = or_([self.c.status==s for s in  ['new','open','stalled']])
        crit = [q]

        crit.extend(query)
        q = and_(crit)
        return self.search(query=q, **kwargs)

    def find_by(self, mapping, **kwargs):
        """Helper function to find tickets based on a dictionary of search terms
        >>> c.ticket.find_by({'owner':'justin'})
        """
        crit = []
        for k, v in mapping.items():
            comp = getattr(self.c,k)==v
            crit.append(comp)

        q = and_(crit)
        return self.search(q, **kwargs)
    def find_by_cf(self, mapping, **kwargs):
        """Helper function to find tickets based on a dictionary of search terms
        >>> c.ticket.find_by_cf({'jack':'B-026A'})
        """
        crit = []
        for k, v in mapping.items():
            comp = getattr(self.c.cf,k)==v
            crit.append(comp)

        q = and_(crit)
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
__all__ = ["Ticket","and_","or_"]
