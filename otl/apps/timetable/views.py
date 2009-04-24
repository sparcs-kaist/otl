# encoding: utf-8
from django.shortcuts import render_to_response
from django.db.models import Count
from django.http import *
from django.template import RequestContext
from django.utils import simplejson as json
from django.conf import settings
from django.core.exceptions import *
from django.contrib.auth.decorators import login_required
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus, Timetable, OverlappingTimeError
from StringIO import StringIO

def index(request):
	if request.user.is_authenticated():
		my_lectures = [_lectures_to_output(Lecture.objects.filter(year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER, timetable__user=request.user, timetable__table_id=id), False) for id in xrange(0,3)]
	else:
		my_lectures = [[], [], []]
	return render_to_response('timetable/index.html', {
		'section': 'timetable',
		'departments': Department.objects.all(),
		'my_lectures': json.dumps(my_lectures, indent=4, ensure_ascii=False),
	}, context_instance=RequestContext(request))

def search(request):
	department = request.GET.get('dept', None)
	year = request.GET.get('year', settings.NEXT_YEAR)
	semester = request.GET.get('term', settings.NEXT_SEMESTER)
	type = request.GET.get('type', None)
	day_begin = request.GET.get('start_day', None)
	day_end = request.GET.get('end_day', None)
	time_begin = request.GET.get('start_time', None)
	time_end = request.GET.get('end_time', None)

	# This query requires Django 1.1 or newer.
	lectures = Lecture.objects.annotate(num_classtimes=Count('classtime')).filter(year=year, semester=semester, num_classtimes__gt=0)
	
	try:
		if department != None:
			lectures = lectures.filter(department__name__exact=department)
		if type != None and type != u'전체보기':
			lectures = lectures.filter(type__exact=type)
		if day_begin != None:
			lectures = lectures.filter(classtime__day__gte=int(day_begin))
		if day_end != None:
			lectures = lectures.filter(classtime__day__lte=int(day_end))
		if time_begin != None:
			lectures = lectures.filter(classtime__begin__gte=ClassTime.numeric_time_to_obj(int(time_begin)))
		if time_end != None:
			lectures = lectures.filter(classtime__end__lte=ClassTime.numeric_time_to_obj(int(time_end)))
	except (TypeError, ValueError):
		return HttpResponseBadRequest()

	lectures = lectures.order_by('type').distinct()

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
	except IntegrityError:
		result = 'DUPLICATED'
	except:
		return HttpResponseServerError()

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
		if lecture_id is None:
			Timetable.objects.filter(user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER, table_id=table_id).delete()
		else:
			lecture = Lecture.objects.get(pk=lecture_id)
			Timetable.objects.get(user=user, lecture=lecture, year=lecture.year, semester=lecture.semester, table_id=table_id).delete()

		lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
		result = 'OK'
	except ObjectDoesNotExist:
		result = 'NOT_EXIST'
	except:
		return HttpResponseServerError()

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
		return HttpResponseServerError()

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
		room = lecture.classtime_set.filter(lecture=lecture, type__exact='l')
		if room.count() > 0:
			room = room[0].room_ko
		else:
			room = ''
		item = {
			'id': lecture.id,
			'year': lecture.year,
			'term': lecture.semester,
			'dept': lecture.department.name,
			'classification': lecture.type,
			'course_no': lecture.old_code,
			'class': lecture.class_no,
			'code': lecture.code,
			'title': lecture.title,
			'lec_time': lecture.num_classes,
			'lab_time': lecture.num_labs,
			'credit': lecture.credit,
			'au': lecture.credit_au,
			'fixed_num': lecture.limit,
			'classroom': room,
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

