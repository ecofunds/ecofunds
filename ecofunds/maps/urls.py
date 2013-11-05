# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('ecofunds.maps.views',
    url(r'^map/$', 'map_view', name='map'),
    url(r'^api/geo/investment/(?:(?P<map_type>\w+)/)?$', 'investment_api', name="investment_api"),
    url(r'^api/geo/project/(?:(?P<map_type>\w+)/)?$', 'project_api', name="project_api"),
    url(r'^api/geo/organization/(?:(?P<map_type>\w+)/)?$', 'organization_api', name="organization_api"),
)
