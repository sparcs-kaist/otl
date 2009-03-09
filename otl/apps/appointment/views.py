# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
	return render_to_response('appointment/index.html', {
		'section': 'appointment',
	}, context_instance=RequestContext(request))
