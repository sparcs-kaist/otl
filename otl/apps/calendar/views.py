# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required
from otl.utils.decorators import login_required_ajax

def index(request):
	if settings.SERVICE_STATUS == 'beta':
		return render_to_response('calendar/beta.html', {
			'section': 'calendar',
			'title': u'일정관리',
		}, context_instance=RequestContext(request))
	else:
		return render_to_response('calendar/index.html', {
			'section': 'calendar',
			'title': u'일정관리',
		}, context_instance=RequestContext(request))

@login_required_ajax
def add_shcedule(request):
	pass

@login_required_ajax
def delete_schedule(request):
	pass

@login_required
def search_schedule(request):
	pass

