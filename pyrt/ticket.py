# pyrt/ticket.py
# Copyright (C) 2007, 2008 Justin Azoff JAzoff@uamail.albany.edu
#
# This module is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.php

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

    def __ge__(self, other):
        return self._compare(self.name, other, '>=')
    def __le__(self, other):
        return self._compare(self.name, other, '<=')

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
    def __init__(self, rtclient, id=None, fields=None):
        self.id=id
        self._fields = fields
        self.rt = rtclient
        self.c = FieldWrapper()
        self.c.cf = FieldWrapper(custom=True)

        self._dirty_fields = {}
        if fields:
            self.id = fields['id']
        self._ticket_initialized = True

    def __repr__(self):
        return "[pyrt.ticket %s]" % self.id

    def search(self, query=None,format='',orderby='id'):
        #print query
        data = self.rt._do('search/ticket', query=query, format=format, orderby=orderby)
        if data and not data[0]:
            return []
        

        #if format=='i':
        #    return [x for x in data.split() if x]
        if format=='l':
            tickets = data
            return [Ticket(self.rt, fields=fields) for fields in tickets]

        if not format:
            ret = []
            data = data[0]
            for k,v in data.items():
                ret.append((k,v))
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
        new_ticket = Ticket(self.rt, id)
        return new_ticket
    def show(self, force=False):
        """Return all the fields for this ticket"""

        if not force and self._fields:
            return self._fields

        fields = self.rt._do('ticket/show', id=self.id)
        self._fields = fields[0]
        return fields[0]
    cache = show

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

    def save(self):
        fields = {}
        fields['id'] = self.id
        fields.update(self._dirty_fields)
        return self.edit(**fields)

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
        r = self.rt._do('ticket/%s/attachments' % self.id)
        if r:
            r = r[0]
            attachments = r['Attachments']
            return [int(x) for x in re.findall('(\d+):', attachments)]

    def get_attachment(self, attachment_id):
        """Fetch a specific attachment associated with this ticket"""
        r = self.rt._do('ticket/%s/attachments/%d' % (self.id, attachment_id))
        if r:
            return r[0]

    def _get_attachments(self):
        for a_id in self.get_attachment_ids():
            yield self.get_attachment(a_id)
    attachments = property(_get_attachments)

    def __getattr__(self, attr):
        if not self.id:
            raise AttributeError, "'Ticket' object has no attribute '%s'" % attr
        self.cache()
        f = self._fields

        if attr in f:
            return f[attr]

        a = attr.replace("_","-") 
        if a in f:
            return f[a]

        raise AttributeError, "'Ticket' object has no attribute '%s'" % attr
    def __getitem__(self, attr):
        f = self._fields
        return f[attr]


    def __setattr__(self, attr, val):
        if not self.__dict__.has_key('_ticket_initialized') or attr == '_fields':
            # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, attr, val)
        self.cache()
        f = self._fields
        if attr in f:
            self._dirty_fields[attr] = val
            f[attr] = val
            return

        a = attr.replace("_","-") 
        if a in f:
            self._dirty_fields[a] = val
            f[a] = val
            return

        raise AttributeError, "'Ticket' object has no attribute '%s'" % attr

__all__ = ["Ticket","and_","or_"]
