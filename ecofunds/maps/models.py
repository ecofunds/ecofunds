from cms.models import CMSPlugin, Page

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core import validators

from gmapi import maps
from gmapi.maps import Geocoder

import pygeoip
import colorsys
import math

from ecofunds import settings

GRADIENT_SPEC = [
        (1.0, 1.0, 1.0),  # white
        (1.0, 0.0, 0.0),  # red
        (0.0, 1.0, 0.0),  # green
        (0.0, 0.0, 1.0),  # blue
        (0.0, 0.0, 0.0)]  # black

class GoogleMapView(object):
    def polygon_sort(self, corners):
        # calculate centroid of the polygon
        n = len(corners) # of corners
        cx = float(sum(x for x, y in corners)) / n
        cy = float(sum(y for x, y in corners)) / n
        # create a new list of corners which includes angles
        cornersWithAngles = []
        for x, y in corners:
            an = (math.atan2(y - cy, x - cx) + 2.0 * math.pi) % (2.0 * math.pi)
            cornersWithAngles.append((x, y, an))
        # sort it using the angles
        cornersWithAngles.sort(key = lambda tup: tup[2])
        # return the sorted corners w/ angles removed
        return map(lambda (x, y, an): (x, y), cornersWithAngles)

    def polygon_area(self, corners):
        n = len(corners) # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1] 
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area

    def polygon_centroid(self, corners):

        #X = SUM[(Xi + Xi+1) * (Xi * Yi+1 - Xi+1 * Yi)] / 6 / A
        #Y = SUM[(Yi + Yi+1) * (Xi * Yi+1 - Xi+1 * Yi)] / 6 / A

        n = len(corners)
        cx = float(sum(x for x, y in corners)) / n
        cy = float(sum(y for x, y in corners)) / n

        #n = corners.count
        #copy = []
        #for x, y in corners:
        #    copy.append((x, y))

        #copy.append(corners[0])

        #xref = 0.0
        #yref = 0.0
        #for i in range(n):
        #    xref += (corners[i][0] + corners[i+1][0]) * (corners[i][0] * corners[i+1][1] - corners[i+1][0] * corners[i][1])
        #    yref += (corners[i][1] + corners[i+1][1]) * (corners[i][0] * corners[i+1][1] - corners[i+1][0] * corners[i][1])

        #area = self.polygon_area(corners)
        #x = xref / 6 / area
        #y = yref / 6 / area

        return cx, cy

    def gradient(self, d, spec=GRADIENT_SPEC):
        N = len(spec)
        idx = int(d * (N - 1))
        t = math.fmod(d * (N - 1), 1.0)
        col1 = colorsys.rgb_to_hsv(*spec[min(N - 1, idx)])
        col2 = colorsys.rgb_to_hsv(*spec[min(N - 1, idx + 1)])
        hsv = tuple(a * (1 - t) + b * t for a, b in zip(col1, col2))
        r, g, b = colorsys.hsv_to_rgb(*hsv)
        return '#%02X%02X%02X' % (r * 255, g * 255, b * 255)

    def get_local_lat_lng(self, request):
        ip = request.META.get('REMOTE_ADDR', None)
        
        gi = pygeoip.GeoIP(settings.GEOIP_DATABASE, pygeoip.STANDARD)
        record = gi.record_by_addr(ip)

        if record:
            lat = record['latitude']
            lng = record['longitude']
            city = '%s, %s' % (record['city'], record['country_name'])
        else:
            lat = -4.521666
            lng = -58.318725
            city = 'Amazonas, Brasil'

        if not lat or not lng:
            geocoder = Geocoder()
            results, status_code = geocoder.geocode({'address': city })
            if results:
                for r in results:
                    lat, lng = r['geometry']['location']['arg']

        return maps.LatLng(lat, lng)

    def get_map(self, request, center_lat_lng=None, zoom=4, mapTypeId=maps.MapTypeId.HYBRID):

        if not center_lat_lng:
            center_lat_lng = self.get_local_lat_lng(request)
        if not zoom:
            zoom = 4
        if not mapTypeId:
            mapTypeId = maps.MapTypeId.HYBRID

        return maps.Map(opts = {
            'center': center_lat_lng,
            'mapTypeId': mapTypeId,
            'zoom': zoom,
            'minZoom': 2,
            'mapTypeControl': False,
            'zoomControl': False,
            'panControl':False,

            'mapTypeControlOptions': {
                 'style': maps.MapTypeControlStyle.HORIZONTAL_BAR
            },
            'streetViewControl': False
        })
class GoogleMapPlugin(CMSPlugin):
    width = models.PositiveIntegerField(_('Width'), help_text=_('Width of map'))
    width_pixels = models.BooleanField(_('Width unit'), choices=((True, 'px'), (False, '%')), default=1, blank=False)

    height = models.PositiveIntegerField(_('Height'), help_text=_('Height of map'))
    height_pixels = models.BooleanField(_('Height unit'), choices=((True, 'px'), (False, '%')), default=1, blank=False)

    show_search_projects = models.BooleanField(_('Show Search Projects'), default=1, blank=False)
    show_search_organizations = models.BooleanField(_('Show Search Organizations'), default=1, blank=False)
    show_search_investments = models.BooleanField(_('Show Search Investments'), default=1, blank=False)