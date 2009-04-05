from django.conf.urls.defaults import *
from otl.apps.favorites import views

urlpatterns = patterns('',
	(ur'^$', views.index),
	(ur'^search/$', views.search),
	(ur'^delete/$', views.delete),
	(ur'^add/$', views.add),
)

