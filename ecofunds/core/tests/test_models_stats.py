# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m
from ecofunds.core.models import Project


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
