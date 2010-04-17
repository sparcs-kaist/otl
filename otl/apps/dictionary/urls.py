from django.conf.urls.defaults import *
from otl.apps.dictionary import views

urlpatterns = patterns('',
    (ur'^$', views.index),
    (ur'^department/(\w+)$', views.department),
    (ur'^search/$', views.search),
    (ur'^view/(\S+)$', views.view),
    (ur'^add_comment/(\d+)$', views.add_comment),
    (ur'^del_comment/(\d+)$', views.delete_comment),
)

