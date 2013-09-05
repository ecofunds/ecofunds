from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

from ecofunds.core.views import *

from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ajax/lookups',include(ajax_select_urls)),
    url(r'^ajax/project/', include('ecofunds.project.urls')),
    url(r'^ajax/organization/', include('ecofunds.organization.urls')),
    url(r'^api/geo/', include('ecofunds.maps.urls')),
    #url(r'^ajax/suggest', GlobalSuggestListView.as_view()),
    url(r'^ajax/suggest', SearchSuggestListView.as_view()),
    url(r'^ajax/upload', uploadify_upload),
    url(r'^map/', include('ecofunds.maps.urls')),
    url(r'^user/',include('ecofunds.user.urls')),
    url(r'^new/$',AttachmentCreateView.as_view(),{},'upload-new'),
    url(r'^', include('cms.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^' + settings.MEDIA_URL.lstrip('/'), include('appmedia.urls')),
    ) + urlpatterns
