# encoding: utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response
from otl.utils import render_page

def home(request):
	return render_to_response('main.html', {
		'title': 'OTL Project',
		'my_variable': 'Hello World!',
	}, context_instance=RequestContext(request))
