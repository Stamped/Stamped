from django.conf.urls.defaults  import patterns, include, url
from django.conf.urls.static    import static
import settings

urlpatterns = patterns('',
    # blog
    url(r'^blog$',                              'core.views.blog'), 
    
    # index
    url(r'^index$',                             'core.views.index'), 
    url(r'^index\.html?$',                      'core.views.index'), 
    url(r'^/?$',                                'core.views.index'), 
    
    # profile
    url(r'^(?P<screen_name>[\w-]{1,20})\/map$', 'core.views.map'), 
    url(r'^(?P<screen_name>[\w-]{1,20})\/?$',   'core.views.profile'), 
)

# static assets
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_DOC_ROOT)

