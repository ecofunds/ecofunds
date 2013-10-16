# coding: utf-8
from django.db.models import Manager, Q


class OrganizationSearchManager(Manager):
    def search(self, **fields):
        qs = self.exclude(location=None, state=None, city=None)
        qs = qs.select_related('location')

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


class ProjectSearchManager(Manager):
    def search(self, **fields):
        qs = self.all()

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(name__icontains=name)|Q(acronym__icontains=name))

        activity = fields.get('activity')
        if activity:
            qs = qs.filter(activities__in=[activity])

        country = fields.get('country')
        if country:
            qs = qs.filter(
                Q(location__name__icontains=country) | Q(location__alternates__icontains=country) | Q(location__country__icontains=country)
            )

        return qs
