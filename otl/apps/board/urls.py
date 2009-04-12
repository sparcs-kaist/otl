from django.conf.urls.defaults import *
from otl.apps.board import views

urlpatterns = patterns('',
	(ur'^lecture/$', views.list_ara),
	(ur'^([^/]+)/$', views.index),
)

