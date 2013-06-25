from django.conf import settings
from django.core.cache import cache
from django.forms.forms import Media
from django.forms.util import flatatt
from django.forms.widgets import Widget
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.simplejson import dumps
from gmapi import maps
from urlparse import urljoin


JQUERY_URL = getattr(settings, 'GMAPI_JQUERY_URL',
                     'http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery'
                     '%s.js' % ('' if settings.DEBUG else '.min'))

MAPS_URL = getattr(settings, 'GMAPI_MAPS_URL',
                   'http://maps.google.com/maps/api/js?sensor=false')

#INFOBUBBLE_URL = 'http://google-maps-utility-library-v3.googlecode.com/svn/trunk/infobubble/src/infobubble.js'
INFOBUBBLE_URL = '%sscripts/maps/%s' % (settings.STATIC_URL, 'infobubble.js')
#MARKERCLUSTERER_URL = 'http://google-maps-utility-library-v3.googlecode.com/svn/trunk/markerclusterer/src/markerclusterer.js'
MARKERCLUSTERER_URL = '%sscripts/maps/%s' % (settings.STATIC_URL, 'markerclusterer.js')

# Same rules apply as ADMIN_MEDIA_PREFIX.
# Omit leading slash to make relative to MEDIA_URL.
MEDIA_PREFIX = getattr(settings, 'GMAPI_MEDIA_PREFIX', 'gmapi/')


class GoogleMap(Widget):
    def __init__(self, attrs=None):
        self.nojquery = (attrs or {}).pop('nojquery', False)
        self.nomapsjs = (attrs or {}).pop('nomapsjs', False)
        self.nostaticimage = (attrs or {}).pop('nostaticimage', False)
        self.noinfobubble = (attrs or {}).pop('noinfobubble', False)

        super(GoogleMap, self).__init__(attrs)

    def render(self, name, gmap, attrs=None):
        if gmap is None:
            gmap = maps.Map()
        default_attrs = {'id': name, 'class': 'gmap'}
        if attrs:
            default_attrs.update(attrs)
        final_attrs = self.build_attrs(default_attrs)

        if final_attrs.has_key('initial'):
            final_attrs.pop('initial')

        width = final_attrs.pop('width', 500)
        width_unit = 'px' if final_attrs.pop('width_pixels', True) else '%'

        height = final_attrs.pop('height', 400)
        height_unit = 'px' if final_attrs.pop('height_pixels', True) else '%'

        style = (u'position:relative;width:%d%s;height:%d%s;' % (width, width_unit, height, height_unit))

        final_attrs['style'] = style + final_attrs.get('style', '')

        map_div = (u'<div style="position:absolute;'
                   u'width:%d%s;height:%d%s"></div>' % (width, width_unit, 100, '%'))

        map_loading = (u'<div class="carregando tela-mapa" style="position:absolute;'
                   u'width:%d%s;"></div>' % (width, width_unit))

        cache.set('gmap_%s' % name, dumps(gmap, separators=(',', ':')))

        map_img = (u'<img style="position:absolute;z-index:1" '
                   u'width="%(x)d%(x_unit)s" height="%(y)d%(y_unit)s" alt="Google Map" '
                   u'src="%(map)s&amp;size=%(x)dx%(y)d" />' %
                   {'map': escape(gmap), 'x': width, 'x_unit': width_unit, 'y': height, 'y_unit': height_unit})

        return mark_safe(u'%s<div%s>%s%s</div>' %
                         (map_loading, flatatt(final_attrs), map_div, map_img if not self.nostaticimage else ''))

    def _media(self):
        js = []
        if not self.nojquery:
            js.append(JQUERY_URL)
        if not self.nomapsjs:
            js.append(MAPS_URL)

        if not self.noinfobubble:
            js.append(INFOBUBBLE_URL)

        js.append(MARKERCLUSTERER_URL)

        js.append(urljoin(MEDIA_PREFIX, 'js/jquery.gmapi%s.js' %
                  ('' if settings.DEBUG else '.min')))
        return Media(js=js)

    media = property(_media)
