# coding: utf-8
from django.test import TestCase
from model_mommy.mommy import make as m


class PlaceCoordinateTest(TestCase):
    def setUp(self):
        l1 = m('Geoname', country='BR', fcode='PCLI', latitude=-10, longitude=-50)

        self.o1 = m('Organization2', name=u'A', kind=1, location=l1)
        self.o2 = m('Project2', name=u'B', kind=1, location=l1, lat=-11, lng=-51)
        self.o3 = m('Organization2', name=u'C', kind=1)

    def test_location_latitude(self):
        self.assertEqual(-10, self.o1.latitude)

    def test_location_longitude(self):
        self.assertEqual(-50, self.o1.longitude)

    def test_custom_latitude(self):
        self.assertEqual(-11, self.o2.latitude)

    def test_custom_latitude(self):
        self.assertEqual(-51, self.o2.longitude)

    def test_no_latitude(self):
        self.assertEqual(None, self.o3.latitude)

    def test_no_longitude(self):
        self.assertEqual(None, self.o3.longitude)
