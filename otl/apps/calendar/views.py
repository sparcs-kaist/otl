# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

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
