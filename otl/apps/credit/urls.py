from django.conf.urls.defaults import *
from otl.apps.credit import views

urlpatterns = patterns('',
        (ur'^$', views.index),
)
