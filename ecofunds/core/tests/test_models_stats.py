# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m
from ecofunds.core.models import Project, Organization


class ProjectStatsTest(TestCase):
    def setUp(self):
        a1 = m('Activity', name='A1')
        a2 = m('Activity', name='A2')

        l1 = m('Location', name='L1')
        l2 = m('Location', name='L2')

        p1 = m('Project', title='P1')
        p1a1 = m('ProjectActivity', entity=p1, activity=a1)
        p1l1 = m('ProjectLocation', entity=p1, location=l1)
        p1l2 = m('ProjectLocation', entity=p1, location=l2)

        p2 = m('Project', title='P2')
        p2a1 = m('ProjectActivity', entity=p2, activity=a1)
        p2l1 = m('ProjectLocation', entity=p2, location=l1)
        p2l2 = m('ProjectLocation', entity=p2, location=l2)

    def test_stats(self):
        expected = {
            'count_projects': 2,
            'count_project_activity_types': 1,
            'count_project_regions': 2,
        }
        self.assertDictEqual(expected, Project.objects.stats())


class OrganizationStatsTest(TestCase):
    def setUp(self):
        t1 = m('OrganizationType', name='T1')
        t2 = m('OrganizationType', name='T2')

        l1 = m('Location', name='L1')
        l2 = m('Location', name='L2')
        l3 = m('Location', name='L3')

        o1 = m('Organization', name='O1', type=t1, state=l1)
        o2 = m('Organization', name='O2', type=t1, state=l2)
        o3 = m('Organization', name='O3', type=t2, state=l3)
        o4 = m('Organization', name='O4', type=t2, state=l3)

    def test_stats(self):
        expected = {
            'count_organizations': 4,
            'count_organization_types': 2,
            'count_organization_regions': 3,
        }
        self.assertDictEqual(expected, Organization.objects.stats())
