from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'www.views.home', name='home'),
    # url(r'^www/', include('www.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(R'^download$', 'teaser.views.download'),
    # url(R'^(?P<screen_name>[\w-]{1,20})/stamps/(?P<stamp_num>\d+)/(?P<stamp_title>[\w-]+)', 'sdetail.views.show'),
    # url(R'^(?P<screen_name>[\w-]{1,20})/mobile/(?P<stamp_num>\d+)/(?P<stamp_title>[\w-]+)', 'sdetail.views.mobile'),
    # url(R'^about$', 'teaser.views.about'),
    # url(R'^privacy-mobile', 'teaser.views.privacy'),
    # url(R'^terms-mobile', 'teaser.views.terms'),
    # url(R'^feedback-mobile', 'teaser.views.feedback'),
    # url(R'^licenses-mobile', 'teaser.views.licenses'),
    # url(R'^faq-mobile', 'teaser.views.faq'),
    # url(R'^pw/(?P<token>[\w-]{36})$',       'appsettings.views.passwordReset'),
    # url(R'^settings/password/forgot$',      'appsettings.views.passwordForgot'),
    # url(R'^settings/password/sent$',        'appsettings.views.passwordSent'),
    # url(R'^settings/password/success$',     'appsettings.views.passwordSuccess'),
    # url(R'^settings/alerts$',               'appsettings.views.alertSettings'),
    # url(R'^settings/alerts/update.json$',   'appsettings.views.alertSettingsUpdate'),
    # url(R'$', 'teaser.views.index'), 
)
