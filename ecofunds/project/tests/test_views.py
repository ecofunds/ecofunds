# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

# reverse(urlname)
# self.client.login(username='', password='')
# self.client.get(url)
# self.client.post(url, {})

class ProjectJSONView(TestCase):
    def test_get_projects(self):
        response = self.client.get(reverse('project_mapsource'))

        self.assertEqual(200, response.status_code)
