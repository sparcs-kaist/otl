from django.conf.urls.defaults import *
from otl.apps.favorites import views

urlpatterns = patterns('',
	(ur'^$', views.index),
	(ur'^add/$', views.add)
)

