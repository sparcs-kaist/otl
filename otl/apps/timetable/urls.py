from django.conf.urls.defaults import *
from otl.apps.timetable import views

js_info_dict = {
        'packages' : ('otl',),
}

urlpatterns = patterns('',
    (ur'^$', views.index),
    (ur'^search/$', views.search),
    (ur'^view/$', views.view_timetable),
    (ur'^add/$', views.add_to_timetable),
    (ur'^delete/$', views.delete_from_timetable),
    (ur'^print/$', views.print_as_pdf),
    (ur'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

