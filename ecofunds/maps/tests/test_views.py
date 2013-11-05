# -*- coding: utf-8 -*-
from decimal import Decimal
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.datetime_safe import datetime
from django.utils.simplejson import dumps, loads

from model_mommy import mommy
m = mommy.make

from ecofunds.core.models import (Country, Location, Project, Organization,
                                  Investment, ProjectLocation)


class ProjectJsonTest(TestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI', latitude=-27.2221329359, longitude=-50.0092212765)

        p1 = m('Project2', name='ProjectA', acronym='PA', location=n1)

        self.resp = self.client.get(reverse('project_api'))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_all(self):
        expected = [dict(id=1, lat=-27.2221329359, lng=-50.0092212765, name="ProjectA", acronym='PA', url=None, link=reverse('project_detail', args=[1]))]
        data = loads(self.resp.content)
        self.assertEqual(data['map']['items'], expected)


class ProjectCsvTest(TestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI', latitude=-27.2221329359, longitude=-50.0092212765)

        p1 = m('Project2', name='ProjectA', acronym='PA', location=n1)

        self.resp = self.client.get(reverse('project_api', args=['csv']))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_header(self):
        self.assertEqual(self.resp.get('Content-Disposition'), 'attachment; filename="projects.csv"')

    def test_csv_header(self):
        expected = 'NAME,ACRONYM,ACTIVITY_TYPE,DESCRIPTION,URL,EMAIL,PHONE,LAT,LNG'
        self.assertIn(expected, self.resp.content)

    def test_csv_data(self):
        expected = 'ProjectA,PA,,,None,None,None,-27.2221329359,-50.0092212765'
        self.assertIn(expected, self.resp.content)


class ProjectXlsTest(TestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI', latitude=-27.2221329359, longitude=-50.0092212765)

        p1 = m('Project2', name='ProjectA', acronym='PA', location=n1)

        self.resp = self.client.get(reverse('project_api', args=['xls']))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_header(self):
        self.assertEqual(self.resp.get('Content-Disposition'), 'attachment; filename="projects.xls"')


class OrganizationJsonTest(TestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI', latitude=-27.2221329359, longitude=-50.0092212765)

        m('Organization2', name=u'Fundo', acronym='Funbio', kind=1, location=n1)
        m('Organization2', name=u'Associacao', acronym='Funbar', kind=1, location=n1)

        self.resp = self.client.get(reverse('organization_api'))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_content(self):
        expected = [
            dict(id=1, name="Fundo", acronym='Funbio', lat=-27.2221329359, lng=-50.0092212765, link=reverse('organization_detail', args=[1])),
            dict(id=2, name="Associacao", acronym='Funbar', lat=-27.2221329359, lng=-50.0092212765, link=reverse('organization_detail', args=[2])),
        ]

        data = loads(self.resp.content)
        self.assertEqual(data['map']['items'], expected)


class OrganizationCsvTest(TestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI', latitude=-27.2221329359, longitude=-50.0092212765)

        m('Organization2', name=u'Fundo', acronym='Funbio', kind=1, location=n1)
        m('Organization2', name=u'Associacao', acronym='Funbar', kind=1, location=n1)

        self.resp = self.client.get(reverse('organization_api', args=['csv']))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_header(self):
        self.assertEqual(self.resp.get('Content-Disposition'), 'attachment; filename="organizations.csv"')

    def test_csv_header(self):
        expected = 'NAME,DESCRIPTION,ORG. TYPE,ADDRESS,ZIPCODE,COUNTRY,STATE,CITY,EMAIL,URL,PHONE,LAT,LNG'
        self.assertIn(expected, self.resp.content)

    def test_csv_content(self):
        l1 = 'Fundo,None,Non-profit,None,None,None,None,None,None,None,None,-27.2221329359,-50.0092212765'
        l2 = 'Associacao,None,Non-profit,None,None,None,None,None,None,None,None,-27.2221329359,-50.0092212765'

        self.assertIn(l1, self.resp.content)
        self.assertIn(l2, self.resp.content)


class OrganizationXlsTest(TestCase):
    def setUp(self):
        n1 = m('Geoname', name=u'Federative Republic of Brazil', alternates='Brasil', country='BR', fcode='PCLI', latitude=-27.2221329359, longitude=-50.0092212765)

        m('Organization2', name=u'Fundo', acronym='Funbio', kind=1, location=n1)
        m('Organization2', name=u'Associacao', acronym='Funbar', kind=1, location=n1)

        self.resp = self.client.get(reverse('organization_api', args=['xls']))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_header(self):
        self.assertEqual(self.resp.get('Content-Disposition'), 'attachment; filename="organizations.xls"')


class InvestmentJsonTest(TestCase):
    def setUp(self):
        n1 = m('Geoname', geonameid=1, name=u'Brazil', country='BR', fcode='PCLI', latitude=-27, longitude=-50)

        p1 = m('Project2', name=u'ProjectA', acronym='PA', location=n1)
        p2 = m('Project2', name=u'ProjectB', acronym='PB', location=n1)

        m('Investment2', kind=1, recipient_project=p1, amount=1000)
        m('Investment2', kind=1, recipient_project=p2, amount=10000)

        self.resp = self.client.get(reverse('investment_api'))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_content(self):
        expected = [
            {
                u'location_id': 1,
                u'lat': -27.0,
                u'lng': -50.0,
                u'total_investment': 11000.0,
                u'total_investment_str': u"$ 11,000.00",
                u'investments': [
                    {
                        u'amount': 1000.0,
                        u'link': u"/detail/investment/1",
                        u'id': 1,
                        u'amount_str': u"$ 1,000.00",
                        u'recipient_name': u"ProjectA"
                    },
                    {
                        u'amount': 10000.0,
                        u'link': u"/detail/investment/2",
                        u'id': 2,
                        u'amount_str': u"$ 10,000.00",
                        u'recipient_name': u"ProjectB"
                    },
                ],

            },
        ]

        data = loads(self.resp.content)
        self.assertEqual(data['map']['items'], expected)


class InvestmentCsvTest(TestCase):
    def setUp(self):
        l1 = m('Geoname', geonameid=1, name=u'Brazil', country='BR', fcode='PCLI', latitude=-27, longitude=-50)

        a1 = m('Activity2', pk=1, name='A1')
        a2 = m('Activity2', pk=2, name='A2')

        m('Investment2',
          kind=1,
          amount=1000,
          recipient_organization__name='RO',
          recipient_project__name='RP',
          recipient_project__acronym='RPA',
          recipient_project__description='RPD',
          recipient_project__activities=[a1, a2],
          recipient_project__geofocus='G',
          recipient_project__location=l1,
          funding_organization__name='FO',
          funding_project__name='FP',
          funding_project__acronym='FPA',
          contributed_at=datetime(2013, 01, 01),
          completed_at=datetime(2013, 12, 01),
        )

        self.resp = self.client.get(reverse('investment_api', args=['csv']))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_header(self):
        self.assertEqual(self.resp.get('Content-Disposition'), 'attachment; filename="investments.csv"')

    def test_csv_header(self):
        expected = 'KIND,AMOUNT,RECP ORG,RECP PROJECT,RECP PROJECT ACRONYM,RECP PROJECT DESC,RECP PROJECT ACTIVITIES,RECP PROJECT GEOFOCUS,FUND ORG,FUND PROJ,FUND PROJ ACRONYM,CONTRIBUTED AT,COMPLETED AT'
        self.assertIn(expected, self.resp.content)

    def test_csv_content(self):
        l1 = 'Donation,1000,RO,RP,RPA,RPD,"A1, A2",G,FO,FP,FPA,2013-01-01,2013-12-01'
        self.assertIn(l1, self.resp.content)


class InvestmentXlsTest(TestCase):
    def setUp(self):
        l1 = m('Geoname', geonameid=1, name=u'Brazil', country='BR', fcode='PCLI', latitude=-27, longitude=-50)

        a1 = m('Activity2', pk=1, name='A1')
        a2 = m('Activity2', pk=2, name='A2')

        m('Investment2',
          kind=1,
          amount=1000,
          recipient_organization__name='RO',
          recipient_project__name='RP',
          recipient_project__acronym='RPA',
          recipient_project__description='RPD',
          recipient_project__activities=[a1, a2],
          recipient_project__geofocus='G',
          recipient_project__location=l1,
          funding_organization__name='FO',
          funding_project__name='FP',
          funding_project__acronym='FPA',
          contributed_at=datetime(2013, 01, 01),
          completed_at=datetime(2013, 12, 01),
        )

        self.resp = self.client.get(reverse('investment_api', args=['xls']))

    def test_status(self):
        self.assertEqual(200, self.resp.status_code)

    def test_header(self):
        self.assertEqual(self.resp.get('Content-Disposition'), 'attachment; filename="investments.xls"')
