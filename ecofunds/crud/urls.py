# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('ecofunds.crud.views',
    url(r'^investments/(?P<pk>\d+)/$', 'investment_detail', name="investment_detail"),
    url(r'^projects/(?P<pk>\d+)/$', 'project_detail', name="project_detail"),
    url(r'^organizations/(?P<pk>\d+)/$', 'organization_detail', name="organization_detail"),
)
