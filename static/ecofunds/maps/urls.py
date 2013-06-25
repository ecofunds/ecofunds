from django.conf.urls.defaults import *
from ecofunds.maps.views import *

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^source/(?P<slug>[-_\w]+)/$', SourceView.as_view()),
)