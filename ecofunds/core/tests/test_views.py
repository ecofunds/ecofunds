# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse as r


class HomeTest(TestCase):
    def test_redirect(self):
        resp = self.client.get(r('home'))
        url = resp['Location']

        self.assertTrue(url.endswith('/map/#investment'))
        self.assertEqual(302, resp.status_code)
