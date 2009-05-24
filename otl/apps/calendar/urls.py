from django.conf.urls.defaults import *
from otl.apps.calendar import views

urlpatterns = patterns('',
	(ur'^$', views.index),
	(ur'^list', views.list_calendar),
	(ur'^modify', views.modify_calendar),
	(ur'^schedule/list', views.list_schedule),
	(ur'^schedule/get', views.get_schedule),
	(ur'^schedule/add', views.add_schedule),
	(ur'^schedule/modify', views.modify_schedule),
	(ur'^schedule/delete', views.delete_schedule),
)

