

from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static    import static
import servers.analytics.settings

import settings
import re
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
    url(r'^stress/$', 'core.views.stress'),
    url(r'^segmentation/$', 'core.views.segmentation'),
    url(r'^trending/$', 'core.views.trending'),
    url(r'^custom/$','core.views.custom'),
    url(r'^/?$', 'core.views.index'), 
)

def custom_static(prefix, view='django.views.static.serve', **kwargs):
    """
        Helper function to return a URL pattern for serving files.
        
        from django.conf import settings
        from django.conf.urls.static import static
        
        urlpatterns = patterns('',
            # ... the rest of your URLconf goes here ...
        ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    """
    
    if prefix and '://' in prefix:
        return []
    elif not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")
    else:
        return patterns('', 
            url(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), view, kwargs=kwargs), 
        )

# static assets
urlpatterns += custom_static(settings.STATIC_URL, document_root=settings.STATIC_DOC_ROOT)