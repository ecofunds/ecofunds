from django.conf.urls.defaults import *
from ecofunds.maps.views import *

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^source/(?P<slug>[-_\w]+)/$', SourceView.as_view()),
    url(r'^investment/(?P<map_type>\w+)', investment_api, name="investment_api"),
    url(r'^project/(?P<map_type>\w+)', project_api, name="project_api"),
    url(r'^organization/(?P<map_type>\w+)', organization_api, name="organization_api"),
    url(r'^(?P<map_type>\w+)', geoapi_map, name='geoapi'),
)
