# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from model_mommy import mommy
m = mommy.make

# reverse(urlname)
# self.client.login(username='', password='')
# self.client.get(url)
# self.client.post(url, {})
