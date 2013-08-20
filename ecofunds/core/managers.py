# coding: utf-8
from django.db.models import Manager, Q


class SearchManager(Manager):
    def search(self, **fields):
        qs = self.exclude(Q(desired_location_lat=None)|Q(desired_location_lng=None))

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(name__icontains=name)|Q(acronym__icontains=name))

        kind = fields.get('kind')
        if kind:
            qs = qs.filter(type=kind)  # Fixme: Rename model field to "kind".

        country = fields.get('country')
        if country:
            qs = qs.filter(country__name__icontains=country)

        state = fields.get('state')
        if state:
            qs = qs.filter(Q(state__iso_sub__icontains=state)|Q(state__name__icontains=state))

        return qs


class ProjectSearchManager(Manager):
    def search(self, **fields):
        qs = self.filter(validated=1)

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(title__icontains=name)|Q(acronym__icontains=name))

        activity = fields.get('activity')
        if activity:
            qs = qs.filter(activities=activity)

        return qs
