# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

def index(request):
	if settings.SERVICE_STATUS == 'beta':
		return render_to_response('appointment/beta.html', {
			'section': 'appointment',
			'title': u'약속 잡기',
		}, context_instance=RequestContext(request))
	else:
		return render_to_response('appointment/index.html', {
			'section': 'appointment',
			'title': u'약속 잡기',
		}, context_instance=RequestContext(request))
	
def view(request, hash):
	pass

def create(request):
	pass
