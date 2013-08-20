# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m
from ecofunds.core.models import Organization, Project


class OrganizationFilterTest(TestCase):
    def setUp(self):
        t1 = m('OrganizationType', pk=1, name='Fundo Ambiental')
        t2 = m('OrganizationType', pk=2, name='Non-profit')

        c1 = m('Country', name='Brazil')
        c2 = m('Country', name='Argentina')

        l1 = m('Location', name='Rio de Janeiro', iso_sub='RJ')
        l2 = m('Location', name='Caminito', iso_sub='CA')

        m('Organization', name=u'Fundação', acronym='Funbio', type=t1, country=c1, state=l1, desired_location_lat=1, desired_location_lng=1)
        m('Organization', name=u'Associacao', acronym='Funbar', type=t1, country=c2, state=l2, desired_location_lat=2, desired_location_lng=2)
        m('Organization', name=u'Fundação', acronym='FIFA', type=t2, country=c2, state=l2, desired_location_lat=2, desired_location_lng=2)
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


class ProjectSearchTest(TestCase):
    def setUp(self):
        m('Project', title=u'Project1', acronym='PRJ1', validated=1)
        m('Project', title=u'Project2', acronym='PRJ2', validated=1)
        m('Project', title=u'Project3', acronym='PRJ3')

    def test_all(self):
        qs = Project.objects.search()
        self.assertPKs(qs, [1, 2])

    def assertPKs(self, qs, values):
        return self.assertQuerysetEqual(qs, values, transform=lambda o: o.pk)
