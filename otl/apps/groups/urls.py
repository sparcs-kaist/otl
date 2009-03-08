from django.conf.urls.defaults import *
from otl.apps.groups import views

urlpatterns = patterns('',
	(ur'^$', views.index),
)

