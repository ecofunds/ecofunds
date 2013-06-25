from django.conf.urls.defaults import *
from ecofunds.opportunity.models import FundingOpportunity

opportunities_dict = {
    'queryset': FundingOpportunity.published.all(),
    'date_field': 'pub_date',
}

opportunities_month_dict = {
    'queryset': FundingOpportunity.published.all(),
    'date_field': 'pub_date',
    'month_format': '%m',
}

urlpatterns = patterns('django.views.generic.date_based',
    (r'^$', 'archive_index', opportunities_dict, 'opportunity_index'),
    (r'^(?P<year>\d{4})/$', 'archive_year', opportunities_dict, 'opportunity_year'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 'archive_month', opportunities_month_dict, 'opportunity_month'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'archive_day', opportunities_month_dict, 'opportunity_day'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 
        'object_detail', opportunities_month_dict, 'opportunity_detail'),
)