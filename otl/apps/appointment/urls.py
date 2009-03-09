from django.conf.urls.defaults import *
from otl.apps.appointment import views

urlpatterns = patterns('',
	(ur'^$', views.index),
)

