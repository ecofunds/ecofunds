# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m
from ecofunds.core.models import Organization


class OrganizationFilterTest(TestCase):
    def setUp(self):
        t1 = m('OrganizationType', pk=1, name='Fundo Ambiental')
        t2 = m('OrganizationType', pk=2, name='Non-profit')

        c1 = m('Country', name='Brazil')
        c2 = m('Country', name='Argentina')

        l1 = m('Location', name='Rio de Janeiro', iso_sub='RJ')
        l2 = m('Location', name='Caminito', iso_sub='CA')

        m('Organization', name=u'Fundação', acronym='Funbio', type=t1, country=c1, state=l1)
        m('Organization', name=u'Associacao', acronym='Funbar', type=t1, country=c2, state=l2)
        m('Organization', name=u'Fundação', acronym='FIFA', type=t2, country=c2, state=l2)

    def test_all(self):
        qs = Organization.objects.search()
        self.assertPKs(qs, [1, 2, 3])

    def test_name(self):
        qs = Organization.objects.search(name='fund')
        self.assertPKs(qs, [1, 3])

        qs = Organization.objects.search(name='funb')
        self.assertPKs(qs, [1, 2])

        qs = Organization.objects.search(name='ssoc')
        self.assertPKs(qs, [2])

        qs = Organization.objects.search(name='if')
        self.assertPKs(qs, [3])

    def test_type(self):
        qs = Organization.objects.search(type=1)
        self.assertPKs(qs, [1, 2])

    def test_country(self):
        qs = Organization.objects.search(country='azi') #Brazil
        self.assertPKs(qs, [1])

    def test_state(self):
        qs = Organization.objects.search(state='RJ')
        self.assertPKs(qs, [1])

        qs = Organization.objects.search(state='Jan')
        self.assertPKs(qs, [1])

    def assertPKs(self, qs, values):
        return self.assertQuerysetEqual(qs, values, transform=lambda o: o.pk)
