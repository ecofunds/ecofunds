from django.conf.urls.defaults import *
from ecofunds.investment.views import *

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^flowsource/(?P<id>\d+)', InvestmentFlowSource.as_view()),
    (r'^mapsource', InvestmentMapSourceView.as_view()),
    (r'^remove',remove_investment),
)
