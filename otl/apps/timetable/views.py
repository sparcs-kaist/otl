# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson as json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus
from StringIO import StringIO

def index(request):
	lectures = Lecture.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER)
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

	lectures = Lectures.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER)
	
	if department != None:
		lectures = lectures.filter(department__name__exact=department)
	if type != None:
		lectures = lectures.filter(type__exact=type)
	if day != None:
		lectures = lectures.filter(classtime__day__exact=day)
	if begin != None:
		lectures = lectures.filter(classtime__begin__exact=ClassTime.numeric_time_to_str(begin))
	if end != None:
		lectures = lectures.filter(classtime__end__exact=ClassTime.numeric_time_to_str(end))

	output = _lectures_to_json(lectures)
	return HttpResponse(output)

@login_required
def add_to_timetable(request):
	user = request.user
	table_id = request.GET.get('table_id', None)
	lecture_id = request.GET.get('lecture_id', None)
	pass

@login_required
def delete_from_timetable(rqeuest):
	user = request.user
	table_id = request.GET.get('table_id', None)
	lecture_id = request.GET.get('lecture_id', None)
	pass

@login_required
def view_timetable(request, user, table_id):
	user = request.user
	table_id = request.GET.get('table_id', None)
	pass


# -- Private functions --

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
			'classroom': lecture.classtime_set.filter(lecture=lecture, type__exact='l')[0].room_ko,
			'prof': lecture.professor,
			'times': [{'day': schedule.day, 'start': schedule.get_begin_numeric(), 'end': schedule.get_end_numeric(), 'classroom': schedule.room_ko, 'type': schedule.get_type_display()} for schedule in lecture.classtime_set.all()],
			'remarks': u'영어강의' if lecture.is_english else u'',
			'examtime': {'day': exam.day, 'start': exam.get_begin_numeric(), 'end': exam.get_end_numeric()} if exam != None else None,
		}
		all.append(item)
	io = StringIO()
	json.dump(all, io, ensure_ascii=False, indent=4)
	return io.getvalue()

