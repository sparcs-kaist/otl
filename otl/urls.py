from django.conf.urls.defaults import *
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (ur'^$', 'otl.apps.main.views.home'),
    (ur'^login/', 'otl.apps.accounts.views.login'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (ur'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './media'}),
    (ur'^admin/(.*)', admin.site.root),
)
