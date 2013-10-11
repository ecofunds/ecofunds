# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('ecofunds.crud.views',
    url(r'^investment/(?P<investment_id>\d+)', 'investment_detail', name="investment_detail"),
    url(r'^project/(?P<project_id>\d+)', 'project_detail', name="project_detail"),
    url(r'^organization/(?P<organization_id>\d+)', 'organization_detail', name="organization_detail"),
)
