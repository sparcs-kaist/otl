# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus

def index(request):
	return render_to_response('timetable/index.html', {
		'section': 'timetable',
		'departments': Department.objects.all(),
	}, context_instance=RequestContext(request))
