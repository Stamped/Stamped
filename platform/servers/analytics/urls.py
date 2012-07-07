from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static    import static
import servers.analytics.settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    url(r'^dashboard/$', 'core.views.index'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^enrichment/$', 'core.views.enrichment'),
    url(r'^latency/$', 'core.views.latency'),
    url(r'^segmentation/$', 'core.views.segmentation'),
    url(r'^trending/$', 'core.views.trending'),
    url(r'^custom/$','core.views.custom'),
    url(r'^/?$', 'core.views.index'), 
)

urlpatterns += static(servers.analytics.settings.STATIC_URL, document_root=servers.analytics.settings.STATIC_DOC_ROOT)