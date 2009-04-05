# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus

def index(request):
	return render_to_response('timetable/index.html', {
		'section': 'timetable',
		'departments': Department.objects.all(),
		'lectures': Lecture.objects.filter(year__exact=settings.CURRENT_YEAR, semester__exact=settings.CURRENT_SEMESTER),
	}, context_instance=RequestContext(request))
