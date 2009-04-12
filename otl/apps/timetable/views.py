# encoding: utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.utils import simplejson as json
from django.conf import settings
from django.core.exceptions import *
from django.contrib.auth.decorators import login_required
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus, Timetable, OverlappingTimeError
from StringIO import StringIO

def index(request):
	lectures = Lecture.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER)
	lectures_output = _lectures_to_output(lectures)
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

	output = _lectures_to_output(lectures)
	return HttpResponse(output)

@login_required
def add_to_timetable(request):
	user = request.user
	table_id = request.GET.get('table_id', None)
	lecture_id = request.GET.get('lecture_id', None)
	
	lectures = []
	try:
		lecture = Lecture.objects.get(pk=lecture_id)
		lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
		for existing_lecture in lectures:
			if existing_lecture.check_classtime_overlapped(lecture):
				raise OverlappingTimeError()
			# We don't check overlapped exam times.
		timetable = Timetable(user=user, lecture=lecture, year=lecture.year, semester=lecture.semester, table_id=table_id)
		timetable.save()

		lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
		result = 'OK'
	except ObjectDoesNotExist:
		result = 'NOT_EXIST'
	except OverlappingTimeError:
		result = 'OVERLAPPED'
	except:
		result = 'ERROR'

	return HttpResponse(json.dumps({
		'result': result,
		'data': _lectures_to_output(lectures, False),
	}, ensure_ascii=False, indent=4))

@login_required
def delete_from_timetable(request):
	user = request.user
	table_id = request.GET.get('table_id', None)
	lecture_id = request.GET.get('lecture_id', None)

	lectures = []
	try:
		lecture = Lecture.objects.get(pk=lecture_id)
		Timetable.objects.get(user=user, lecture=lecture, year=lecture.year, semester=lecture.semester, table_id=table_id).delete()
		lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
		result = 'OK'
	except ObjectDoesNotExist:
		result = 'NOT_EXIST'
	except:
		result = 'ERROR'

	return HttpResponse(json.dumps({
		'result': result,
		'data': _lectures_to_output(lectures, False),
	}, ensure_ascii=False, indent=4))

@login_required
def view_timetable(request):
	user = request.user
	table_id = request.GET.get('table_id', None)

	lectures = []
	try:
		lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
		result = 'OK'
	except ObjectDoesNotExist:
		result = 'OK'
	except:
		result = 'ERROR'

	return HttpResponse(json.dumps({
		'result': result,
		'data': _lectures_to_output(lectures, False),
	}, ensure_ascii=False, indent=4))


# -- Private functions --

def _lectures_to_output(lectures, conv_to_json=True):
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
	if conv_to_json:
		io = StringIO()
		json.dump(all, io, ensure_ascii=False, indent=4)
		return io.getvalue()
	else:
		return all

