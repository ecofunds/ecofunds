# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m
from ecofunds.core.models import Organization


class OrganizationFilterTest(TestCase):
    def setUp(self):
        m('Organization', name=u'Fundação', acronym='Funbio')
        m('Organization', name=u'Associacao', acronym='Funbio')
        m('Organization', name=u'Fundação', acronym='FIFA')

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

    def assertPKs(self, qs, values):
        return self.assertQuerysetEqual(qs, values, transform=lambda o: o.pk)
