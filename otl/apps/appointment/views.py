# encoding: utf-8
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from otl.apps.appointment.models import Appointment, Participating, CandidateTimeRange, ParticipatingTimeRange
from otl.apps.appointment.forms import CreateForm
from otl.utils.forms import DateTimeRange

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

@login_required
def view(request, hash):
	try:
		appointment = Appointment.objects.get(hash=hash)
	except Appointment.DoesNotExist:
		return HttpResponseNotFound()
	
	# Determine the mode.
	if appointment.completed:
		mode = 'completed'
	else:
		if request.user.id == appointmnet.owner.id:
			mode = 'owner'
		else:
			mode = 'participant'
	
	# Initialize variables according to the current mode.
	all_confirmed = False
	final_appointment_shcedule = None
	time_ranges_of_others = []
	submit_caption = u'참여 가능 시간 확정하기'
	submit_operation = u'participate'
	
	# The owner is also a participant, so we just create the relationship.
	try:
		p = Participating.objects.get(participant=request.user, appointment=appointment)
	except Participating.DoesNotExist:
		p = Participating()
		p.participant = request.user
		p.appointment = appointment
		p.confirmed = False
		p.save()

	# Collect all participating time ranges of the appointment.
	# NOTE: Some of them may overlap with others.
	time_ranges_of_others = ParticipatingTimeRange.objects.filter(belongs_to__appointment=appointment)

	# If this appointment is already finished, just show the finalized schedule.
	if mode == 'completed':
		final_appointment_schedule = DateTimeRange(appointment.date, appointment.time_start, appointment.time_end)
		all_confirmed = True
		submit_caption = u'(이미 완료됨)'
		submit_operation = u''
	else:
		# Check if all participants have confirmed.
		num_participants = Participating.objects.filter(appointment=appointment).count()
		all_confirmed = (num_participants > 0 and num_participants == Participating.objects.filter(appointment=appointment, confirmed=True).count())

		# If all participants have confirmed and the current user is the owner,
		# make the onwer able to finalize the appointment.
		if all_confirmed and mode == 'owner':
			submit_caption = u'약속 시간 최종 확정하기'
			submit_operation = u'finalize'

	return render_to_response('appointment/view.html', {
		'section': 'appointment',
		'title': u'약속 잡기',
		'mode': json.dumps(mode),
		'all_confirmed': json.dumps(all_confirmed),
		'final_appointment_schedule': json.dumps(final_appointment_schedule),
		'my_schedules': json.dumps(my_schedules),
		'time_ranges_of_others': json.dumps(time_ranges_of_others),
		'submit_operation': submit_oepration,
		'submit_caption': submit_caption,
	}, context_instance=RequestContext(request))

@login_required
def change(request):
	if request.method == 'POST':
		# TODO: implement adding ParticipatingTimeRange...
		f = ChangeForm(request.POST):
		if f.is_valid():
			op = f.cleaned_data['submit_operation']
			if op == 'participate':
				pass
			elif op == 'finalize':
				pass
			else:
				return HttpResponseBadRequest()
		else:
			return HttpResponseBadRequest()
	else:
		return HttpResponseBadRequest()

@login_required
def create(request):
	err = u''
	if request.method == 'POST':
		f = CreateForm(request.POST)
		if f.is_valid():
			# Creates the appointment item
			key = u''.join([random.choice('ABCEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyz') for i in xrange(32)])
			a = Appointment()
			a.owner = request.user
			a.hash = key
			a.save()

			# Adds candidate time ranges
			for range in f.cleaned_data['time_ranges']:
				c = CandidateTimeRange()
				c.belongs_to = a
				c.date = range.date
				c.time_start = range.time_start
				c.time_end = range.time_end
				c.save()

			return HttpResponseRedirect('/appointment/view/%s' % key)
		else:
			err = u'내용을 올바로 입력해주세요.'
	else:
		f1 = CreateForm()
	return render_to_response('appointment/create.html', {
		'section': 'appointment',
		'title': u'약속 만들기',
		'create_step1_form': f1,
		'error_msg': err,
	}, context_instance=RequestContext(request))
