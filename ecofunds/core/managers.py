# coding: utf-8
from django.db.models import Manager, Q, Sum


class SearchManager(Manager):
    def search(self, **fields):
        qs = self.exclude(Q(desired_location_lat=None)|Q(desired_location_lng=None))
        qs = qs.select_related('type', 'state')

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


class ProjectLocationSearchManager(Manager):
    def search(self, **fields):
        qs = self.select_related('entity', 'location')
        qs = qs.filter(entity__validated=1)

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(entity__title__icontains=name)|Q(entity__acronym__icontains=name))

        activity = fields.get('activity')
        if activity:
            qs = qs.filter(entity__activities=activity)

        country = fields.get('country')
        if country:
            qs = qs.filter(location__country__name__icontains=country)

        state = fields.get('state')
        if state:
            qs = qs.filter(Q(location__iso_sub__icontains=state)|Q(location__name__icontains=state))

        org = fields.get('organization')
        if org:
            qs = qs.filter(Q(entity__organization__name__icontains=org)|Q(entity__organization__acronym__icontains=org))

        return qs

    def search_investment(self, **fields):
        qs = self.select_related('entity', 'location', 'country')
        qs = qs.filter(entity__validated=1)
        qs = qs.annotate(entity_amount=Sum('entity__recipient_investments__amount_usd')).exclude(entity_amount=None)

        return qs
