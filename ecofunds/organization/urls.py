from django.conf.urls.defaults import *
from ecofunds.organization.views import *

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^suggest', OrganizationSuggestListView.as_view(data_type="html")),
    (r'^mapsource', OrganizationMapSourceView.as_view()),
    (r'^chartsource', OrganizationChartSourceView.as_view()),
    (r'^remove',remove_organization),
)
