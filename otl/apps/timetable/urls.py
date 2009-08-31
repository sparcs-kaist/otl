from django.conf.urls.defaults import *
from otl.apps.timetable import views

urlpatterns = patterns('',
    (ur'^$', views.index),
    (ur'^search/$', views.search),
    (ur'^view/$', views.view_timetable),
    (ur'^add/$', views.add_to_timetable),
    (ur'^delete/$', views.delete_from_timetable),
)

