from django.conf.urls.defaults import *
from otl.apps.accounts import views

urlpatterns = patterns('',
    (ur'^myinfo/$', views.myinfo),
    (ur'^auth/$', views.SSO_authenticate),
    (ur'^agree/$', views.after_agreement),
)
