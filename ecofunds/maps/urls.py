from django.conf.urls.defaults import *
from ecofunds.maps.views import *

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^source/(?P<slug>[-_\w]+)/$', SourceView.as_view()),
    (r'^(?P<map_type>\w+)', geoapi_map),
)
