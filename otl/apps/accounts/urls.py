from django.conf.urls.defaults import *
from otl.apps.accounts import views

urlpatterns = patterns('',
    (ur'^myinfo/$', views.myinfo),
    (ur'^view/(\w+)$', views.view),
)
