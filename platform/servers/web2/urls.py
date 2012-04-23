from django.conf.urls.defaults import patterns, include, url
import settings

urlpatterns = patterns('',
    # static assets
    (R'^assets/(?P<path>.*)$',      'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}), 
    
    # blog
    url(R'^blog$',                  'core.views.blog'), 
    
    # index
    url(R'$',                       'core.views.index'), 
)

