# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus
try:
	import json
except:
	import simplejson as json

def index(request):
	lectures = Lecture.objects.filter(year__exact=settings.CURRENT_YEAR, semester__exact=settings.CURRENT_SEMESTER)
	lectures_output = _lectures_to_json(lectures)
	return render_to_response('timetable/index.html', {
		'section': 'timetable',
		'departments': Department.objects.all(),
		'lectures_json': lectures_output,
	}, context_instance=RequestContext(request))

def lecture_filter(request):
	department = request.GET.get('dept', None)
	type = request.GET.get('type', None)
	day = request.GET.get('day', None)
	begin = request.GET.get('start', None)
	end = request.GET.get('end', None)

	lectures = Lectures.objects.all()
	
	if department != None:
		lectures = lectures.filter(department__name__exact=department)
	if type != None:
		lectures = lectures.filter(type__exact=type)
	if day != None:
		lectures = lectures.classtime_set.filter(day__exact=day)
	if begin != None:
		lectures = lectures.classtime_set.filter(begin__exact=ClassTime.numeric_time_to_str(begin))
	if end != None:
		lectures = lectures.classtime_set.filter(end__exact=ClassTime.numeric_time_to_str(end))

	output = _lectures_to_json(lectures)
	return HttpResponse(output)

def _lectures_to_json(lectures):
	all = []
	for lecture in lectures:
		try:
			exam = lecture.examtime_set.get() # 첫번째 항목만 가져옴
		except:
			exam = None
		item = {
			'id': lecture.id,
			'year': lecture.year,
			'term': lecture.semester,
			'dept': lecture.department.name,
			'classification': lecture.type,
			'course_no': lecture.code,
			'class': lecture.class_no,
			'code': lecture.get_code_numeric(),
			'title': lecture.title,
			'lec_time': lecture.num_classes,
			'lab_time': lecture.num_labs,
			'credit': lecture.credit,
			'au': lecture.credit_au,
			'fixed_num': lecture.limit,
			'prof': lecture.professor,
			'times': [{'day': schedule.day, 'start': schedule.get_begin_numeric(), 'end': schedule.get_end_numeric(), 'classroom': schedule.room_ko, 'type': schedule.get_type_display()} for schedule in lecture.classtime_set.all()],
			'remarks': u'영어강의' if lecture.is_english else u'',
			'examtime': {'day': exam.day, 'start': exam.get_begin_numeric(), 'end': exam.get_end_numeric()} if exam != None else None,
		}
		all.append(item)
	return json.dumps(all, indent=4)

