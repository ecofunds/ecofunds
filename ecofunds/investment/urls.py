from django.conf.urls.defaults import *
from ecofunds.investment.views import *

urlpatterns = patterns('django.views.generic.list_detail',
    (r'^flowsource/(?P<id>\d+)', InvestmentFlowSource.as_view()),
    url(r'^mapsource', InvestmentMapSourceView.as_view(), name='investment_mapsource'),
    (r'^remove',remove_investment),
    (r'^density', ajax_density_view),
)
