from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
        (r'^login/$','django.contrib.auth.views.login',{'template_name':'user/login.html','extra_context':{'next':'/'}}),
        (r'^logout/$','django.contrib.auth.views.logout',{'next_page':'/'}),
        (r'^validate/(?P<user>\d+)/(?P<code>\w+)/$','ecofunds.user.views.validate'),
        )
