# -*- coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.utils.translation import ugettext
def index(request):
    return render_to_response('credit/index.html', {
        'section' : 'credit',
        'title' : ugettext(u'학점 계산기'),
        }, context_instance=RequestContext(request))
