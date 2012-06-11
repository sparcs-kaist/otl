from django.conf.urls.defaults import *
from otl.apps.dictionary import views

urlpatterns = patterns('',
    (ur'^$', views.index),
    (ur'^department/(\w+)$', views.department),
    (ur'^search/$', views.search),
    (ur'^view/(\w+)/$', views.view),
    (ur'^add_comment/$', views.add_comment),
    (ur'^del_comment/$', views.delete_comment),
    (ur'^add_summary/$', views.add_summary),
)

