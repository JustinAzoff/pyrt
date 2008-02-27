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
        nullops = {'=': 'IS', '!=': 'IS NOT'}
        if other is None:
            other = 'NULL'
            op = nullops[op]
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

class Ticket(object):
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
        """Fetch a ticket"""
        if 'ticket/' in str(id):
            id = int(id.replace('ticket/',''))
        new_ticket = Ticket(self.rt)
        new_ticket.id = id
        return new_ticket
    def show(self):
        """Return all the fields for this ticket"""
        page = self.rt._do('ticket/show', id=self.id)
        data = self.rt.split_res(page)
        return forms.parse(data)[0]
    def create(self, **fields):
        """Create a new ticket
           >>> rt.ticket.new(queue='trouble', subject=subject, requestor=requestor, Text=text,
                   cf={
                    'building': building_name,
                    'room':     room_number,
                   })
        """

        self.id = 'new'
        out = self.edit(**fields)
        match = re.search("200 Ok\n\n.*Ticket (\d+) created",out, re.MULTILINE)
        if match:
            id = match.groups()[0]
            self.id = id
            return self
        raise Exception("Error creating ticket %s" % out)

    def edit(self, **fields):
        """Edit an existing ticket
           >>> t = rt.ticket.get(123)
           >>> t.edit(subject='new subject')
        """
        fields['id'] = self.id
        content = forms.generate(fields)
        page = self.rt._do('ticket/edit', content=content)
        return page

    def _comment(self, action, message, cc=None, bcc=None):
        fields = {
            'Action': action,
            'Ticket': self.id,
            'Cc'    : cc,
            'Bcc'   : bcc,
            'Text'  : message,
            }
        content = forms.generate(fields)
        page = self.rt._do('ticket/%s/comment' % self.id, content=content)
        return page

    def comment(self, message, cc=None, bcc=None):
        """Comment on a ticket"""
        return self._comment('comment', message, cc, bcc)

    def correspond(self, message, cc=None, bcc=None):
        """Correspond on a ticket"""
        return self._comment('correspond', message, cc, bcc)

    def _ticket_action(self, action):
        fields = {
            'Action': action,
            }
        content = forms.generate(fields)
        page = self.rt._do('ticket/%s/take' % self.id, content=content)
        return page

    def take(self):
        return self._ticket_action('take')
    def untake(self):
        return self._ticket_action('untake')
    def steal(self):
        return self._ticket_action('steal')

    def get_attachment_ids(self):
        """Return a list of attachment ids for this ticket"""
        page = self.rt._do('ticket/%s/attachments' % self.id)
        data = self.rt.split_res(page)
        r =  forms.parse(data)
        if r:
            r = r[0]
            attachments = r['Attachments']
            return [int(x) for x in re.findall('(\d+):', attachments)]

    def get_attachment(self, attachment_id):
        """Fetch a specific attachment associated with this ticket"""
        page = self.rt._do('ticket/%s/attachments/%d' % (self.id, attachment_id))
        data = self.rt.split_res(page)
        r =  forms.parse(data)
        if r:
            return r[0]

    def _get_attachments(self):
        for a_id in self.get_attachment_ids():
            yield self.get_attachment(a_id)
    attachments = property(_get_attachments)


__all__ = ["Ticket","and_","or_"]
