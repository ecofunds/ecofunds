# coding: utf-8
from django.db.models import Manager, Q


class SearchManager(Manager):
    def search(self, **fields):
        qs = self.get_query_set()

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(name__icontains=name)|Q(acronym__icontains=name))

        return qs
