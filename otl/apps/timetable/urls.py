from django.conf.urls.defaults import *
from otl.apps.timetable import views

urlpatterns = patterns('',
	(ur'^$', views.index),
	(ur'^ajax/lecture-filter$', views.lecture_filter),
	(ur'^ajax/view/$', views.view_timetable),
	(ur'^add/$', views.add_to_timetable),
	(ur'^delete/$', views.delete_from_timetable),
)

