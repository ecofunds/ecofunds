from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings

from ecofunds.core.views import Home

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name='home'),
    url(r'', include('ecofunds.maps.urls')),
    url(r'', include('ecofunds.crud.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^select2/", include("django_select2.urls")),
)
