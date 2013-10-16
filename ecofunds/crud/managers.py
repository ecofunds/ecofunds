# coding: utf-8
from django.db.models import Manager, Q


class OrganizationSearchManager(Manager):
    def search(self, **fields):
        qs = self.exclude(country=None, state=None, city=None)
        qs = qs.select_related('country', 'state', 'city')

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(name__icontains=name)|Q(acronym__icontains=name))

        kind = fields.get('kind')
        if kind:
            qs = qs.filter(kind=kind)

        country = fields.get('country')
        if country:
            qs = qs.filter(
                Q(location__name__icontains=country) | Q(location__alternates__icontains=country) | Q(location__country__icontains=country)
            )

        return qs
