# -*- coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.http import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import simplejson as json
from otl.apps.appointment.models import Appointment, Participating, CandidateTimeRange, ParticipatingTimeRange
from otl.apps.appointment.forms import CreateForm, ChangeForm
from otl.utils.forms import DateTimeRange
import random

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
        if request.user.id == appointment.owner.id:
            mode = 'owner'
        else:
            mode = 'participant'

    # Initialize variables according to the current mode.
    all_confirmed = False
    final_appointment_schedule = None
    candidate_time_ranges = []
    time_ranges_of_others = []
    submit_caption = u'참여 가능 시간 확정하기'
    submit_operation = u'participate-confirm'

    # The owner is also a participant, so we just create the relationship.
    try:
        p = Participating.objects.get(participant=request.user, appointment=appointment)
    except Participating.DoesNotExist:
        p = Participating()
        p.participant = request.user
        p.appointment = appointment
        p.confirmed = False
        p.save()

    # Collect other participants' participating time ranges of the appointment.
    # NOTE: Some of them may overlap with others.
    for item in ParticipatingTimeRange.objects.filter(Q(belongs_to__appointment=appointment) & ~Q(belongs_to__participant=request.user)):
        time_ranges_of_others.append({
            'date': item.date.strftime('%Y-%m-%d'),
            'time_start': item.time_start.hour * 60 + item.time_start.minute,
            'time_end': item.time_end.hour * 60 + item.time_end.minute,
        })

    # Collect the candidate time ranges.
    for item in CandidateTimeRange.objects.filter(belongs_to=appointment):
        candidate_time_ranges.append({
            'date': item.date.strftime('%Y-%m-%d'),
            'time_start': item.time_start.hour * 60 + item.time_start.minute,
            'time_end': item.time_end.hour * 60 + item.time_end.minute,
        })

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
        'candidate_time_ranges': json.dumps(candidate_time_ranges),
        'time_ranges_of_others': json.dumps(time_ranges_of_others),
        'submit_operation': submit_operation,
        'submit_caption': submit_caption,
    }, context_instance=RequestContext(request))

@login_required
def change(request):
    """
    Changes the state of the participating appointment.
    Perform necessary processes according to the operation parameter.

    Request: use POST parameters
    - operation : string; "participate-confirm" | "finalize"
    - time_ranges : string repr of array of DateTimeRange

    """
    if request.method == 'POST':
        f = ChangeForm(request.POST)
        if f.is_valid():
            op = f.cleaned_data['operation']
            hash = f.cleaned_data['hash']
            time_ranges = f.cleaned_data['time_ranges']
            try:
                appointment = Appointment.objects.get(hash=hash)
            except Appointment.DoesNotExist:
                return HttpResponseNotFound()

            if op == 'participate-confirm':
                # Mark as the participant(current user) confirmed.
                participating_relation = Participating.objects.get(participant=request.user, apppointment=appointment)
                participating_relation.confirmed = True
                participating_relation.save()

                # Users may change their participating times after their first confirms.
                # So delete previous participating time ranges if exist.
                ParticipatingTimeRange.objects.filter(belongs_to=participating_relation).delete()

                # Add new participating time ranges.
                for t in time_ranges:
                    p = ParticipatingTimeRange()
                    p.belongs_to = participating_relation
                    p.date = t.date
                    p.time_start = t.time_start
                    p.time_end = t.time_end
                    p.save()

            elif op == 'finalize':
                # Check again if all participants confirmed.
                num_participants = Participating.objects.filter(appointment=appointment).count()
                if not (num_participants > 0 and num_participants == Participating.objects.filter(appointment=appointment, confirmed=True).count()):
                    return HttpResponseForbidden('Not allowed to finalize before all participants confirm.')

                # Use the time_ranges parameter as the final appointment time decided.
                t = time_ranges[0]
                appointment.date = t.date
                appointment.time_start = t.time_start
                appointment.time_end = t.time_end

                # Make the appointment completed.
                appointment.completed = True
                appointment.save()

                # Clean up all participating relations for this appointment.
                Participating.objects.filter(appointment=appointment).delete()

            else:
                return HttpResponseBadRequest('Invalid operation.')
        else:
            return HttpResponseBadRequest('Invliad parameters.')
    else:
        return HttpResponseBadRequest('Invalid request.')

@login_required
def create(request):
    err_msg = u''
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
            err_msg = u'시간대를 선택하지 않았거나, 요약이 빠졌습니다.'
    else:
        f = CreateForm()
    return render_to_response('appointment/create.html', {
        'section': 'appointment',
        'title': u'약속 만들기',
        'create_form': f,
        'err_msg': err_msg,
    }, context_instance=RequestContext(request))

