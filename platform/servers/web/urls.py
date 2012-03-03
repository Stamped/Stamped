from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    # DOWNLOAD!
    url(R'^download$',                      'teaser.views.download'),
    url(R'^download/$',                     'teaser.views.download'),

    # Tweet Pages
    url(R'^(?P<screen_name>[\w-]{1,20})/stamps/(?P<stamp_num>\d+)/(?P<stamp_title>[\w-]+)', 'sdetail.views.show'),
    url(R'^(?P<screen_name>[\w-]{1,20})/mobile/(?P<stamp_num>\d+)/(?P<stamp_title>[\w-]+)', 'sdetail.views.mobile'),

    # Settings
    url(R'^pw/(?P<token>[\w-]{36})$',       'appsettings.views.passwordReset'),
    url(R'^settings/password/forgot$',      'appsettings.views.passwordForgot'),
    url(R'^settings/password/sent$',        'appsettings.views.passwordSent'),
    url(R'^settings/password/success$',     'appsettings.views.passwordSuccess'),
    url(R'^settings/alerts$',               'appsettings.views.alertSettings'),
    url(R'^settings/alerts/update.json$',   'appsettings.views.alertSettingsUpdate'),

    # Mobile Pages
    url(R'^privacy-mobile',                 'teaser.views.mobilePrivacy'),
    url(R'^terms-mobile',                   'teaser.views.mobileTerms'),
    url(R'^feedback-mobile',                'teaser.views.mobileFeedback'),
    url(R'^licenses-mobile',                'teaser.views.mobileLicenses'),
    url(R'^faq-mobile',                     'teaser.views.mobileFaq'),

    # Website
    url(R'^about$',                         'teaser.views.about'),
    url(R'^faq$',                           'teaser.views.faq'),
    url(R'^privacy$',                       'teaser.views.privacy'),
    url(R'^terms-of-service$',              'teaser.views.terms'),
    url(R'^blog$',                          'teaser.views.blog'),
    
    url(R'^maps/sxsw$',                     'maps.views.sxsw'),
    url(R'^maps/test$',                     'maps.views.test'),
    url(R'^maps/sxsw.json$',                     'maps.views.sxsw_json'),
    
    # Index
    url(R'$',                               'teaser.views.index'), 
)
