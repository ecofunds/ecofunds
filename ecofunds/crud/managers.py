# coding: utf-8
from django.db.models import Manager, Q
from ecofunds.geonames.models import Geoname


class PlaceSearchManager(Manager):
    def filter_place(self, qs, **fields):

        country = fields.get('country')
        if country:
            cs = Geoname.objects.countries(Q(name__icontains=country) | Q(alternates__icontains=country) | Q(country__icontains=country))
            cs = cs.values_list('country')

            qs = qs.filter(Q(location__country__in=cs))

        state = fields.get('state')
        if state:
            cs = Geoname.objects.states(Q(name__icontains=state) | Q(alternates__icontains=state))
            cs = cs.values_list('country', 'admin1')

            ors = Q()
            for pair in cs:
                c, a = pair
                ors |= Q(location__country=c, location__admin1=a)
            qs = qs.filter(ors)

        city = fields.get('city')
        if city:
            qs = qs.filter(Q(location__fcode='ADM2') & (Q(location__name__icontains=city) | Q(location__alternates__icontains=city)))

        return qs


class OrganizationSearchManager(PlaceSearchManager):
    def search(self, **fields):
        qs = self.exclude(location=None)
        qs = qs.select_related('location')

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(name__icontains=name)|Q(acronym__icontains=name))

        kind = fields.get('kind')
        if kind:
            qs = qs.filter(kind=kind)

        qs = self.filter_place(qs, **fields)

        return qs

class ProjectSearchManager(PlaceSearchManager):
    def search(self, **fields):
        qs = self.exclude(location=None)
        qs = qs.select_related('location')

        name = fields.get('name')
        if name:
            qs = qs.filter(Q(name__icontains=name)|Q(acronym__icontains=name))

        activity = fields.get('activity')
        if activity:
            qs = qs.filter(activities__in=[activity])

        org = fields.get('organization')
        if org:
            qs = qs.filter(Q(organization__name__icontains=org)|Q(organization__acronym__icontains=org))

        qs = self.filter_place(qs, **fields)

        return qs


class InvestmentSearchManager(Manager):
    def search(self, **fields):
        qs = self.all()

        kind = fields.get('kind')
        if kind:
            qs = qs.filter(kind=kind)

        project = fields.get('project')
        if project:
            qs = qs.filter(Q(funding_project__name__icontains=project)|Q(funding_project__acronym__icontains=project)|
                           Q(recipient_project__name__icontains=project)|Q(recipient_project__acronym__icontains=project))

        org = fields.get('organization')
        if org:
            qs = qs.filter(Q(funding_organization__name__icontains=org)|Q(funding_organization__acronym__icontains=org)|
                           Q(recipient_organization__name__icontains=org)|Q(recipient_organization__acronym__icontains=org))

        country = fields.get('country')
        if country:
            qs = qs.filter(
                Q(recipient_organization__location__name__icontains=country) |
                Q(recipient_organization__location__alternates__icontains=country) |
                Q(recipient_organization__location__country__icontains=country)
            )

        return qs

