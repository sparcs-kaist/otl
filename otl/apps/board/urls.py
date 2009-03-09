from django.conf.urls.defaults import *
from otl.apps.board import views

urlpatterns = patterns('',
	(ur'^lecture/$', views.index_ara),
	(ur'^([^/]+)/$', views.index),
)

