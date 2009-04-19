from django.conf.urls.defaults import *
from otl.apps.groups import views

urlpatterns = patterns('',
	(ur'^$', views.index),
	(ur'^create/$', views.create),
	(ur'^morelist/$', views.morelist),
	(ur'^search/$', views.search),
	(ur'^join/(\d+)$', views.join),
	(ur'^withdraw/(\d+)$', views.withdraw),
#	(ur'^list/(\d+)$', views.list),
)

