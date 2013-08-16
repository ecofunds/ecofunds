# coding: utf-8
from django.db.models import Manager, Q


class SearchManager(Manager):
    def search(self, **fields):
        qs = self.get_query_set()

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(name__icontains=name)|Q(acronym__icontains=name))

        type_ = fields.get('type')
        if type_:
            qs = qs.filter(type=type_)

        country = fields.get('country')
        if country:
            qs = qs.filter(country__name__icontains=country)

        return qs
