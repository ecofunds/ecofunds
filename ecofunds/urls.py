from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.conf import settings

from ecofunds.core.views import Home

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/geo/', include('ecofunds.maps.urls')),
    url(r'^map/', include('ecofunds.maps.urls')),
    url(r'^user/',include('ecofunds.user.urls')),
    url(r'^', include('cms.urls')),
    url(r"^select2/", include("django_select2.urls")),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls')),
    ) + urlpatterns
