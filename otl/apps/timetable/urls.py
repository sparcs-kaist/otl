from django.conf.urls.defaults import *
from otl.apps.timetable import views

urlpatterns = patterns('',
	(ur'^$', views.index),
)

