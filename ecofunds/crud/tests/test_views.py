# -*- coding: utf-8 -*-
from decimal import Decimal

from django.test import TestCase
from django.core.urlresolvers import reverse as r

from model_mommy.mommy import make as m

from ecofunds.crud.models import Project2, Organization2, Investment2


class HomeTest(TestCase):
    def setUp(self):
        self.activity = m('Activity2', name="Some Activity")
        self.organization_fund = m('Organization2', name='Funding Org X')
        self.organization_recp = m('Organization2', name='Recp Org X')
        self.project_fund = m('Project2', name='Fund Project X',
                                          activities=[self.activity],
                                          organization=self.organization_fund)
        self.project_recp = m('Project2', name='Recp Project Y',
                                          activities=[self.activity],
                                          organization=self.organization_recp)
        self.investment = m('Investment2',
                            funding_organization=self.organization_fund,
                            funding_project=self.project_fund,
                            recipient_organization=self.organization_recp,
                            recipient_project=self.project_recp,
                            amount=Decimal(900000))


    def test_organization_detail(self):
        response1 = self.client.get(r('organization_detail', args=[1]))
        response2 = self.client.get(r('organization_detail', args=[2]))

        self.assertEquals(200, response1.status_code)
        self.assertTrue('Funding Org X' in response1.content)
        self.assertEquals(200, response2.status_code)
        self.assertTrue('Recp Org X' in response2.content)

    def test_project_detail(self):
        response1 = self.client.get(r('project_detail', args=[1]))
        response2 = self.client.get(r('project_detail', args=[2]))

        self.assertEquals(200, response1.status_code)
        self.assertTrue('Fund Project X' in response1.content)
        self.assertEquals(200, response2.status_code)
        self.assertTrue('Recp Project Y' in response2.content)

    def test_investment_detail(self):
        response = self.client.get(r('investment_detail', args=[1]))

        self.assertEquals(200, response.status_code)
        self.assertTrue(self.organization_fund.name in response.content)
        self.assertTrue(self.organization_recp.name in response.content)
        self.assertTrue(self.project_fund.name in response.content)
        self.assertTrue(self.project_recp.name in response.content)
        self.assertTrue('900,000.00' in response.content)

