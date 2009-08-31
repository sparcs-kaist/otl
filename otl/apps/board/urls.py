from django.conf.urls.defaults import *
from otl.apps.board import views

urlpatterns = patterns('',
    (ur'^lecture/$', views.list_ara),
    (ur'^lecture/(\d+)/$', views.read_ara),
    (ur'^([^/]+)/$', views.index),
)

