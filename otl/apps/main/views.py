# -*- coding: utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect

from django import template
template.add_to_builtins('django.templatetags.i18n')

def home(request):
    return render_to_response('main.html', {
        'title': 'OTL Project',
        'section': 'home',
        'my_variable': 'Hello World!',
    }, context_instance=RequestContext(request))

def about(request):
    return render_to_response('about.html', {
        'title': u'만든 사람들',
        'section': u'info',
    }, context_instance=RequestContext(request))

def changelanguage(request):
    if (not 'django_language' in request.session) or request.session['django_language'] == 'ko':
        request.session['django_language'] = 'en'
    else:
        request.session['django_language'] = 'ko'
    if request.user.is_authenticated():
        if request.session['django_language'] == 'ko':
            request.user.userprofile.language = 'ko-KR'
        else:
            request.user.userprofile.language = 'en-US'
        request.user.userprofile.save()
    return HttpResponseRedirect('/')
