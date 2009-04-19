from django.conf.urls.defaults import *
from django.contrib import admin
from django.http import HttpResponseRedirect

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (ur'^$', lambda request: HttpResponseRedirect('/favorites/')),
    (ur'^login/', 'otl.apps.accounts.views.login'),
    (ur'^logout/', 'otl.apps.accounts.views.logout'),

    (ur'^timetable/', include('otl.apps.timetable.urls')),
    (ur'^calendar/', include('otl.apps.calendar.urls')),
    (ur'^appointment/', include('otl.apps.appointment.urls')),
    (ur'^groups/', include('otl.apps.groups.urls')),
	(ur'^favorites/', include('otl.apps.favorites.urls')),
    (ur'^board/', include('otl.apps.board.urls')),

    (ur'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './media'}),
    (ur'^admin/(.*)', admin.site.root),
)
