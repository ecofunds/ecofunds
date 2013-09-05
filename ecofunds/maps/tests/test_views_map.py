# coding: utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse as r
from ecofunds.maps.forms import InvestmentFilterForm, OrganizationFilterForm, ProjectFilterForm


class MapViewTest(TestCase):
    fixtures = ['pages.json']

    def setUp(self):
        self.resp = self.client.get(r('map'))

    def test_get(self):
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(self.resp, "maps/map.html")

    def test_forms(self):
        self.assertBoundedForm('search_project_form', ProjectFilterForm)
        self.assertBoundedForm('search_organization_form', OrganizationFilterForm)
        self.assertBoundedForm('search_investment_form', InvestmentFilterForm)

    def test_context(self):
        expected = ('count_projects', 'count_project_activity_types', 'count_project_regions',
                    'count_organizations', 'count_organization_types', 'count_organization_regions',
                    'count_investments', 'count_organization_investments', 'count_investment_types',
                    'count_recipient_organization', 'count_recipient_entity_investments')

        self.assertContextVariables(expected, self.resp.context)

    def assertContextVariables(self, expected, context):
        for var in expected:
            self.assertIn(var, context)

    def assertBoundedForm(self, context_var, klass):
        form = self.resp.context[context_var]
        self.assertIsInstance(form, klass)
        self.assertTrue(form.is_bound)
