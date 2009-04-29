# encoding: utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response

def home(request):
	return render_to_response('main.html', {
		'title': 'OTL Project',
		'section': 'home',
		'my_variable': 'Hello World!',
	}, context_instance=RequestContext(request))

def about(request):
	return render_to_response('about.html', {
		'title': u'개발자 노트',
		'section': u'info',
	}, context_instance=RequestContext(request))
