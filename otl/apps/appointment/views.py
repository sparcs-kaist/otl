# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from otl.apps.appointment.models import Appointment, Participating, CandidateTimeRange, ParticipatingTimeRange
from otl.apps.appointment.forms import CreateStep1Form

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
	return render_to_response('appointment/view.html', {
		'section': 'appointment',
		'title': u'약속 잡기',
	}, context_instance=RequestContext(request))

def create(request):
	err = u''
	if request.method == 'POST':
		f1 = CreateStep1Form(request.POST)
		if f1.is_valid():
			# TODO: implement
			pass
		else:
			err = u'내용을 올바로 입력해주세요.'
	else:
		f1 = CreateStep1Form()
	return render_to_response('appointment/create.html', {
		'section': 'appointment',
		'title': u'약속 만들기',
		'create_step1_form': f1,
		'error_msg': err,
	}, context_instance=RequestContext(request))
