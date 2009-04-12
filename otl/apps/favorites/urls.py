from django.conf.urls.defaults import *
from otl.apps.favorites import views

urlpatterns = patterns('',
	(ur'^$', views.index),
	(ur'^search/$', views.search),
	(ur'^delete/(\d+)$', views.delete),
	(ur'^add/(\d+)$', views.add),
	(ur'^create/$', views.create),
	(ur'^morelist/$', views.morelist),
)

