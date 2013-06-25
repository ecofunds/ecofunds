from django.conf.urls.defaults import *
from ecofunds.project.views import *

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^suggest', ProjectSuggestListView.as_view(data_type="html")),
    (r'^countries', CountriesSuggestListView.as_view(data_type="html")),
    (r'^regions', RegionsSuggestListView.as_view(data_type="html")),
    (r'^list', ProjectListView.as_view(template_name='project/list.html')),
    (r'^excel', ProjectFilteredListExcel.as_view()),
    (r'^resumes', ProjectListView.as_view(template_name='project/resumes.html')),
    (r'^mapsource', ProjectMapSourceView.as_view()),
    (r'^chartsource', ProjectChartSourceView.as_view()),
    (r'^geoip', GeoIpView.as_view()),
    (r'^remove',remove_project),
)
