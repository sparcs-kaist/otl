from django.conf.urls.defaults import *
from otl.apps.calendar import views

urlpatterns = patterns('',
	(ur'^$', views.index),
)

