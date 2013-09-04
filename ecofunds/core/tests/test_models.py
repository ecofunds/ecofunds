# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m
from ecofunds.core.models import (Organization, ProjectLocation, Country,
                                  Location, Project)



class OrganizationModelTest(TestCase):
    def setUp(self):
        self.org = m('Organization', name=u'Fundo', acronym='Funbio',
            type__name='Fundo Ambiental', state__name='Rio de Janeiro',
            phone_country_prefix='55', phone_local_prefix='21', phone_number='22222222')

    def test_formated_phone_number_property(self):
        self.assertEqual('55 21 22222222', self.org.formated_phone_number)

    def test_kind_property(self):
        self.assertEqual('Fundo Ambiental', self.org.kind)

    def test_location_name_property(self):
        self.assertEqual('Rio de Janeiro', self.org.location_name)


class OrganizationFilterTest(TestCase):
    def setUp(self):
        t1 = m('OrganizationType', pk=1, name='Fundo Ambiental')
        t2 = m('OrganizationType', pk=2, name='Non-profit')

        c1 = m('Country', name='Brazil')
        c2 = m('Country', name='Argentina')

        l1 = m('Location', name='Rio de Janeiro', iso_sub='RJ')
        l2 = m('Location', name='Caminito', iso_sub='CA')

        m('Organization', name=u'Fundo', acronym='Funbio', type=t1, country=c1, state=l1, desired_location_lat=1, desired_location_lng=1)
        m('Organization', name=u'Associacao', acronym='Funbar', type=t1, country=c2, state=l2, desired_location_lat=2, desired_location_lng=2)
        m('Organization', name=u'Fundao', acronym='FIFA', type=t2, country=c2, state=l2, desired_location_lat=2, desired_location_lng=2)
        m('Organization', name=u'Outro', acronym='OT', type=t2, country=c2, state=l2, desired_location_lat=None, desired_location_lng=None)

    def test_all(self):
        '''No filter, return all Organizations with desired lat and lng.'''
        qs = Organization.objects.search()
        self.assertPKs(qs, [1, 2, 3])

    def test_name(self):
        '''Filter by name or acronym.'''
        qs = Organization.objects.search(name='fund')
        self.assertPKs(qs, [1, 3])

        qs = Organization.objects.search(name='funb')
        self.assertPKs(qs, [1, 2])

        qs = Organization.objects.search(name='ssoc')
        self.assertPKs(qs, [2])

        qs = Organization.objects.search(name='if')
        self.assertPKs(qs, [3])

    def test_kind(self):
        '''Filter by type.'''
        qs = Organization.objects.search(kind=1)
        self.assertPKs(qs, [1, 2])

    def test_country(self):
        '''Filter by country.'''
        qs = Organization.objects.search(country='azi') #Brazil
        self.assertPKs(qs, [1])

    def test_state(self):
        '''Filter by state.'''
        qs = Organization.objects.search(state='RJ')
        self.assertPKs(qs, [1])

        qs = Organization.objects.search(state='Jan')
        self.assertPKs(qs, [1])

    def assertPKs(self, qs, values):
        return self.assertQuerysetEqual(qs, values, transform=lambda o: o.pk)


class ProjectModelTest(TestCase):
    def setUp(self):
        country = m(Country, name="Brasil")
        location = m(Location, id=1, country=country, name="Rio de Janeiro",
                     centroid="-22.5331067902,-43.2435698976",
                     polygon="")
        funding_org = m(Organization, name="Funding Ord", country=country,
                        state=location, validated=True, desired_location_lat=-22.882778, desired_location_lng=-43.103889)
        organization = m(Organization, name="Funbio", country=country,
                         state=location, validated=True, desired_location_lat=-22.880766, desired_location_lng=-43.104335)
        self.project = m(Project, main_organization=organization,
                                  title="Projeto de Teste",
                                  acronym="Projeto de Teste",
                                  locations=[],
                                  centroid="-27.2221329359,-50.0092212765",
                                  validated=True)

    def test_project_lat_property(self):
        self.assertEqual(-27.2221329359, self.project.lat)

    def test_project_lng_property(self):
        self.assertEqual(-50.0092212765, self.project.lng)


class ProjectLocationSearchTest(TestCase):
    def setUp(self):
        t1 = m('Activity', pk=1)
        t2 = m('Activity', pk=2)

        l1 = m('Location', pk=1, name='Rio de Janeiro', iso_sub='RJ', country__name='Brazil')
        l2 = m('Location', pk=2, name='Caminito', iso_sub='CA', country__name='Argentina')
        l3 = m('Location', pk=3, name='Mato Grosso', iso_sub='MT', country__name='Brazil')
        l4 = m('Location', pk=4, name='Fortaleza', iso_sub='CE', country__name='Brazil')

        o1 = m('Organization', name=u'Fundo', acronym='Funbio')
        o2 = m('Organization', name=u'Federação', acronym='FIFA')

        p1 = m('Project', title=u'ProjectA', acronym='PA', validated=1)
        p2 = m('Project', title=u'ProjectB1', acronym='PB1', validated=1)
        p3 = m('Project', title=u'ProjectB2', acronym='PB2', validated=1)
        p4 = m('Project', title=u'ProjectC', acronym='PC')

        # Nota: entity é PK, logo, não é possível um Projeto ter + de 1 activity no banco atual.
        m('ProjectActivity', entity=p1, activity=t1)
        m('ProjectActivity', entity=p2, activity=t2)
        m('ProjectActivity', entity=p3, activity=t2)

        m('ProjectLocation', entity=p1, location=l1)
        m('ProjectLocation', entity=p1, location=l3)
        m('ProjectLocation', entity=p1, location=l4)
        m('ProjectLocation', entity=p2, location=l1)
        m('ProjectLocation', entity=p3, location=l2)
        m('ProjectLocation', entity=p4, location=l2)

        m('ProjectOrganization', entity=p1, organization=o1)
        m('ProjectOrganization', entity=p2, organization=o2)
        m('ProjectOrganization', entity=p3, organization=o1)
        m('ProjectOrganization', entity=p4, organization=o2)

    def test_all(self):
        qs = ProjectLocation.objects.search()
        self.assertLocationPKs(qs, [1, 3, 4, 1, 2])

    def test_name(self):
        '''Filter by name or acronym.'''
        qs = ProjectLocation.objects.search(name='ectB')
        self.assertEntityLocations(qs, [(2, 1), (3, 2)])

        qs = ProjectLocation.objects.search(name='PB')
        self.assertEntityLocations(qs, [(2, 1), (3, 2)])

        qs = ProjectLocation.objects.search(name='ectA')
        self.assertEntityLocations(qs, [(1, 1), (1, 3), (1,4)])

        qs = ProjectLocation.objects.search(name='PB2')
        self.assertEntityLocations(qs, [(3, 2)])

    def test_activity(self):
        '''Filter by activity.'''
        qs = ProjectLocation.objects.search(activity=1)
        self.assertEntityLocations(qs, [(1,1), (1,3), (1,4)])

        qs = ProjectLocation.objects.search(activity=2)
        self.assertEntityLocations(qs, [(2,1), (3,2)])

    def test_country(self):
        '''Filter by country.'''
        qs = ProjectLocation.objects.search(country='azi') #Brazil
        self.assertEntityLocations(qs, [(1,1), (1,3), (1,4), (2,1)])

    def test_state(self):
        '''Filter by state.'''
        qs = ProjectLocation.objects.search(state='RJ')
        self.assertEntityLocations(qs, [(1,1), (2,1)])

        qs = ProjectLocation.objects.search(state='Jan')
        self.assertEntityLocations(qs, [(1,1), (2,1)])

    def test_organization(self):
        '''Filter by organization name or acronym'''
        qs = ProjectLocation.objects.search(organization='Fed')
        self.assertEntityLocations(qs, [(2,1)])

        qs = ProjectLocation.objects.search(organization='Funb')
        self.assertEntityLocations(qs, [(1,1), (1,3), (1,4), (3,2)])

    def assertPKs(self, qs, values):
        return self.assertQuerysetEqual(qs, values, transform=lambda o: o.location.pk)

    def assertLocationPKs(self, qs, values):
        return self.assertQuerysetEqual(qs, values, lambda o: o.location.pk)

    def assertEntityLocations(self, qs, values):
        return self.assertQuerysetEqual(qs, values, lambda o: (o.entity.pk, o.location.pk))


class InvestmentSearchTest(TestCase):
    def setUp(self):
        t1 = m('InvestmentType', pk=1)

        l1 = m('Location', pk=1, name='Rio de Janeiro', iso_sub='RJ', country__name='Brazil')

        p1 = m('Project', title=u'ProjectA', acronym='PA', validated=1)
        p2 = m('Project', title=u'ProjectC', acronym='PC') # invalid
        p3 = m('Project', title=u'ProjectB2', acronym='PB2', validated=1) # without investment
        p4 = m('Project', title=u'ProjectB1', acronym='PB1', validated=1)

        m('ProjectLocation', entity=p1, location=l1)
        m('ProjectLocation', entity=p2, location=l1)
        m('ProjectLocation', entity=p3, location=l1)
        m('ProjectLocation', entity=p4, location=l1)

        m('Investment', recipient_entity=p1, amount_usd=1)
        m('Investment', recipient_entity=p4, amount_usd=1, type=t1)
        m('Investment', recipient_entity=p4, amount_usd=2)

    def test_all(self):
        qs = ProjectLocation.objects.search_investment()
        expected = [(1, 1, 1), (1, 4, 3)]

        self.assertResult(qs, expected)

    def test_kind(self):
        '''Filter by investment type'''
        qs = ProjectLocation.objects.search_investment(kind=1)
        expected = [(1, 4, 1)]
        self.assertResult(qs, expected)

    def test_project(self):
        '''Filter by project name or acronym'''
        qs = ProjectLocation.objects.search_investment(project='ectB')
        self.assertResult(qs, [(1, 4, 3)])

        qs = ProjectLocation.objects.search_investment(project='PB')
        self.assertResult(qs, [(1, 4, 3)])

    def assertResult(self, qs, expected):
        return self.assertQuerysetEqual(qs, expected,
            lambda o: (o.location.pk, o.entity.pk, o.entity_amount))
