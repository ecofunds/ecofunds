# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m
from ecofunds.crud.models import Organization2, Project2, Investment2


class BaseTestCase(TestCase):
    def assertPKs(self, qs, values):
        data = map(lambda o: o.pk, qs)
        return self.assertSetEqual(set(data), set(values))


class OrganizationFilterTest(BaseTestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI')
        n2 = m('Geoname', name=u'Argentine', alternates='Argentina', country='AR', fcode='PCLI')

        m('Organization2', name=u'Fundo', acronym='Funbio', kind=1, location=n1)
        m('Organization2', name=u'Associacao', acronym='Funbar', kind=1, location=n2)
        m('Organization2', name=u'Fundao', acronym='FIFA', kind=2, location=n2)
        m('Organization2', name=u'Hidden', acronym='HD')

    def test_all(self):
        '''No filter, return all Organizations with desired lat and lng.'''
        qs = Organization2.objects.search()
        self.assertPKs(qs, [1, 2, 3])

    def test_name(self):
        '''Filter by name or acronym.'''
        qs = Organization2.objects.search(name='fund')
        self.assertPKs(qs, [1, 3])

        qs = Organization2.objects.search(name='funb')
        self.assertPKs(qs, [1, 2])

        qs = Organization2.objects.search(name='ssoc')
        self.assertPKs(qs, [2])

        qs = Organization2.objects.search(name='if')
        self.assertPKs(qs, [3])

    def test_kind(self):
        '''Filter by type.'''
        qs = Organization2.objects.search(kind=1)
        self.assertPKs(qs, [1, 2])

    def test_pk(self):
        '''Special filter by pk'''
        qs = Organization2.objects.search(pk=1)
        self.assertPKs(qs, [1])


class OrganizationLocationFilterTest(BaseTestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI')
        n2 = m('Geoname', name=u'Argentine', alternates='Argentina', country='AR', fcode='PCLI')

        s1 = m('Geoname', name=u'Rio de Janeiro', alternates='RJ', country='BR', fcode='ADM1', admin1='21')
        s2 = m('Geoname', name=u'Buenos Aires', alternates='BA', country='AR', fcode='ADM1', admin1='22')

        c1 = m('Geoname', name=u'Niteroi', alternates='Nictheroy', country='BR', fcode='ADM2', admin1='21')
        c2 = m('Geoname', name=u'Caminito', alternates='Caminito', country='AR', fcode='ADM2', admin2='22')

        m('Organization2', name=u'OrgA', acronym='OA', location=n1)
        m('Organization2', name=u'OrgB', acronym='OB', location=s1)
        m('Organization2', name=u'OrgC', acronym='OC', location=c1)
        m('Organization2', name=u'OrgD', acronym='OD', location=n2)
        m('Organization2', name=u'OrgE', acronym='OE', location=s2)
        m('Organization2', name=u'OrgF', acronym='OF', location=c2)

    def test_country(self):
        '''Filter by country.'''
        qs = Organization2.objects.search(country='azi') #Brazil
        self.assertPKs(qs, [1, 2, 3])

        qs = Organization2.objects.search(country='asi') #Brasil
        self.assertPKs(qs, [1, 2, 3])

        qs = Organization2.objects.search(country='br') #BR
        self.assertPKs(qs, [1, 2, 3])

    def test_state(self):
        '''Filter by state'''
        qs = Organization2.objects.search(state='RJ')
        self.assertPKs(qs, [2, 3])

        qs = Organization2.objects.search(state='Jan')
        self.assertPKs(qs, [2, 3])

    def test_city(self):
        '''Filter by city.'''
        qs = Organization2.objects.search(city='iter') #Niteroi
        self.assertPKs(qs, [3])

        qs = Organization2.objects.search(city='ther') #Nictheroy
        self.assertPKs(qs, [3])


class ProjectFilterTest(BaseTestCase):
    def setUp(self):
        a1 = m('Activity2', pk=1)
        a2 = m('Activity2', pk=2)

        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI')
        n2 = m('Geoname', name=u'Argentine', alternates='Argentina', country='AR', fcode='PCLI')

        o1 = m('Organization2', name=u'Fundo', acronym='Funbio')
        o2 = m('Organization2', name=u'Federação', acronym='FIFA')

        p1 = m('Project2', name='ProjectA', acronym='PA', activities=[a1], location=n1, organization=o1)
        p2 = m('Project2', name='ProjectB1', acronym='PB1', activities=[a2], location=n1, organization=o2)
        p3 = m('Project2', name='ProjectB2', acronym='PB2', activities=[a2], location=n2)
        p4 = m('Project2', name='ProjectC', acronym='PC')

    def test_all(self):
        qs = Project2.objects.search()
        self.assertPKs(qs, [1, 2 ,3])

    def test_name(self):
        '''Filter by name or acronym.'''
        qs = Project2.objects.search(name='ectB')
        self.assertPKs(qs, [2, 3])

        qs = Project2.objects.search(name='PB')
        self.assertPKs(qs, [2, 3])

        qs = Project2.objects.search(name='ectA')
        self.assertPKs(qs, [1])

        qs = Project2.objects.search(name='PB2')
        self.assertPKs(qs, [3])

    def test_activity(self):
        '''Filter by activity.'''
        qs = Project2.objects.search(activity=1)
        self.assertPKs(qs, [1])

        qs = Project2.objects.search(activity=2)
        self.assertPKs(qs, [2, 3])

    def test_organization(self):
        '''Filter by organization name or acronym'''
        qs = Project2.objects.search(organization='Funb')
        self.assertPKs(qs, [1])

        qs = Project2.objects.search(organization='Fund')
        self.assertPKs(qs, [1])

    def test_pk(self):
        '''Special filter by pk'''
        qs = Project2.objects.search(pk=1)
        self.assertPKs(qs, [1])


class ProjectLocationFilterTest(BaseTestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI')
        n2 = m('Geoname', name=u'Argentine', alternates='Argentina', country='AR', fcode='PCLI')

        s1 = m('Geoname', name=u'Rio de Janeiro', alternates='RJ', country='BR', fcode='ADM1', admin1='21')
        s2 = m('Geoname', name=u'Buenos Aires', alternates='BA', country='AR', fcode='ADM1', admin1='22')

        c1 = m('Geoname', name=u'Niteroi', alternates='Nictheroy', country='BR', fcode='ADM2', admin1='21')
        c2 = m('Geoname', name=u'Caminito', alternates='Caminito', country='AR', fcode='ADM2', admin2='22')

        m('Project2', name=u'OrgA', acronym='OA', location=n1)
        m('Project2', name=u'OrgB', acronym='OB', location=s1)
        m('Project2', name=u'OrgC', acronym='OC', location=c1)
        m('Project2', name=u'OrgD', acronym='OD', location=n2)
        m('Project2', name=u'OrgE', acronym='OE', location=s2)
        m('Project2', name=u'OrgF', acronym='OF', location=c2)

    def test_country(self):
        '''Filter by country.'''
        qs = Project2.objects.search(country='azi') #Brazil
        self.assertPKs(qs, [1, 2, 3])

        qs = Project2.objects.search(country='asi') #Brasil
        self.assertPKs(qs, [1, 2, 3])

        qs = Project2.objects.search(country='br') #BR
        self.assertPKs(qs, [1, 2, 3])

    def test_state(self):
        '''Filter by state'''
        qs = Project2.objects.search(state='RJ')
        self.assertPKs(qs, [2, 3])

        qs = Project2.objects.search(state='Jan')
        self.assertPKs(qs, [2, 3])

    def test_city(self):
        '''Filter by city.'''
        qs = Project2.objects.search(city='iter') #Niteroi
        self.assertPKs(qs, [3])

        qs = Project2.objects.search(city='ther') #Nictheroy
        self.assertPKs(qs, [3])


class InvestmentFilterTest(BaseTestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI')
        s1 = m('Geoname', name=u'Rio de Janeiro', alternates='RJ', country='BR', fcode='ADM1', admin1='21')

        o1 = m('Organization2', name=u'Fundo', acronym='Funbio', location=n1)
        p1 = m('Project2', name='ProjectA', acronym='PA', location=s1)

        i1 = m('Investment2', kind=1, recipient_project=p1, recipient_organization=o1)
        i2 = m('Investment2', kind=2, recipient_project=p1, recipient_organization=o1) # Parent
        i3 = m('Investment2', kind=2, recipient_project=p1, recipient_organization=o1, parent=i2)
        i4 = m('Investment2', kind=2, funding_project=p1, funding_organization=o1) # No recipient_project
        i5 = m('Investment2', kind=2) # No recipient_project

    def test_all(self):
        qs = Investment2.objects.search()
        self.assertPKs(qs, [1, 3])

    def test_kind(self):
        '''Filter by investment type'''
        qs = Investment2.objects.search(kind=1)
        self.assertPKs(qs, [1])

    def test_project(self):
        '''Filter by project name or acronym'''
        qs = Investment2.objects.search(project='ectA')
        self.assertPKs(qs, [1, 3])

        qs = Investment2.objects.search(project='PA')
        self.assertPKs(qs, [1, 3])

    def test_organization(self):
        '''Filter by organization name or acronym'''
        qs = Investment2.objects.search(organization='Fund')
        self.assertPKs(qs, [1, 3])

        qs = Investment2.objects.search(organization='Funb')
        self.assertPKs(qs, [1, 3])

    def test_pk(self):
        '''Special filter by pk'''
        qs = Investment2.objects.search(pk=1)
        self.assertPKs(qs, [1])

class InvestmentLocationFilterTest(BaseTestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI')
        n2 = m('Geoname', name=u'Argentine', alternates='Argentina', country='AR', fcode='PCLI')

        s1 = m('Geoname', name=u'Rio de Janeiro', alternates='RJ', country='BR', fcode='ADM1', admin1='21')
        s2 = m('Geoname', name=u'Buenos Aires', alternates='BA', country='AR', fcode='ADM1', admin1='22')

        c1 = m('Geoname', name=u'Niteroi', alternates='Nictheroy', country='BR', fcode='ADM2', admin1='21')
        c2 = m('Geoname', name=u'Caminito', alternates='Caminito', country='AR', fcode='ADM2', admin2='22')

        p1 = m('Project2', name=u'ProjectA', acronym='PA', location=n1)
        p2 = m('Project2', name=u'ProjectB', acronym='PB', location=s1)
        p3 = m('Project2', name=u'ProjectC', acronym='PC', location=c1)
        p4 = m('Project2', name=u'ProjectD', acronym='PD', location=n2)
        p5 = m('Project2', name=u'ProjectE', acronym='PE', location=s2)
        p6 = m('Project2', name=u'ProjectF', acronym='PF', location=c2)

        m('Investment2', kind=1, recipient_project=p1)
        m('Investment2', kind=2, recipient_project=p2)
        m('Investment2', kind=2, recipient_project=p3)
        m('Investment2', kind=2)

    def test_country(self):
        '''Filter by country.'''
        qs = Investment2.objects.search(country='azi') #Brazil
        self.assertPKs(qs, [1, 2, 3])

        qs = Investment2.objects.search(country='asi') #Brasil
        self.assertPKs(qs, [1, 2, 3])

        qs = Investment2.objects.search(country='br') #BR
        self.assertPKs(qs, [1, 2, 3])

    def test_state(self):
        '''Filter by state'''
        qs = Investment2.objects.search(state='RJ')
        self.assertPKs(qs, [2, 3])

        qs = Investment2.objects.search(state='Jan')
        self.assertPKs(qs, [2, 3])

    def test_city(self):
        '''Filter by city.'''
        qs = Investment2.objects.search(city='iter') #Niteroi
        self.assertPKs(qs, [3])

        qs = Investment2.objects.search(city='ther') #Nictheroy
        self.assertPKs(qs, [3])
