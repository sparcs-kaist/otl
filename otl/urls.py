from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (ur'^$', lambda request: HttpResponseRedirect('/timetable/')),
    (ur'^login/', 'otl.apps.accounts.views.login'),
    (ur'^logout/', 'otl.apps.accounts.views.logout'),
    (ur'^changelanguage/', 'otl.apps.main.views.changelanguage'),

    (ur'^timetable/', include('otl.apps.timetable.urls')),
    (ur'^accounts/', include('otl.apps.accounts.urls')),
    (ur'^about/', 'otl.apps.main.views.about'),
    (ur'^help/', 'otl.apps.main.views.help'),
    (ur'^dictionary/', include('otl.apps.dictionary.urls')),

    (ur'^favicon.ico$', lambda request: HttpResponseNotFound()),

    (ur'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './media'}),
    (ur'^admin/',include(admin.site.urls)),
)
