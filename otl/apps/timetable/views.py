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
	if settings.DEBUG:
		my_lectures_output = json.dumps(my_lectures, indent=4, ensure_ascii=False)
	else:
		my_lectures_output = json.dumps(my_lectures, ensure_ascii=False, sort_keys=False, separators=(',',':'))
	return render_to_response('timetable/index.html', {
		'section': 'timetable',
		'title': u'모의시간표',
		'departments': Department.objects.all(),
		'my_lectures': my_lectures_output,
		'lecture_list': _lectures_to_output(_search(dept=u'2044', type=u'전체보기'))
	}, context_instance=RequestContext(request))

def search(request):
	try:
		# Convert QueryDict to a normal python dict.
		q = {}
		for key, value in request.GET.iteritems():
			q[str(key)] = value
		output = _lectures_to_output(_search(**q))
		return HttpResponse(output)
	except ValidationError:
		return HttpResponseBadRequest()

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

def _search(**conditions):
	department = conditions.get('dept', None)
	year = conditions.get('year', settings.NEXT_YEAR)
	semester = conditions.get('term', settings.NEXT_SEMESTER)
	type = conditions.get('type', None)
	day_begin = conditions.get('start_day', None)
	day_end = conditions.get('end_day', None)
	time_begin = conditions.get('start_time', None)
	time_end = conditions.get('end_time', None)

	# This query requires Django 1.1 or newer.
	lectures = Lecture.objects.annotate(num_classtimes=Count('classtime')).filter(year=year, semester=semester, num_classtimes__gt=0)
	
	try:
		if department == u'-1' and type == u'전체보기':
			raise ValidationError()
		if department != None and department != u'-1':
			lectures = lectures.filter(department__id__exact=int(department))
		if type != None and type != u'전체보기':
			lectures = lectures.filter(type__exact=type)
		if day_begin != None and day_end != None and time_begin != None and time_end != None:
			if day_begin == day_end:
				lectures = lectures.filter(classtime__day__exact=int(day_begin),
				                           classtime__begin__gte=ClassTime.numeric_time_to_obj(int(time_begin)),
				                           classtime__end__lte=ClassTime.numeric_time_to_obj(int(time_end)))
			else:
				lectures = lectures.filter(classtime__day__gte=int(day_begin), classtime__day__lte=int(day_end),
				                           classtime__begin__gte=ClassTime.numeric_time_to_obj(int(time_begin)),
				                           classtime__end__lte=ClassTime.numeric_time_to_obj(int(time_end)))
	except (TypeError, ValueError):
		raise ValidationError()

	return lectures.filter(deleted=False).order_by('type', 'code').distinct()

def _lectures_to_output(lectures, conv_to_json=True):
	all = []
	for lecture in lectures:
		try:
			exam = lecture.examtime_set.get() # 첫번째 항목만 가져옴
		except:
			exam = None
		room = ClassTime.objects.filter(lecture=lecture, type__exact='l')
		if room.count() > 0:
			room = room[0].get_location()
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
			'deleted': lecture.deleted,
			'prof': lecture.professor,
			'times': [{'day': schedule.day, 'start': schedule.get_begin_numeric(), 'end': schedule.get_end_numeric(), 'classroom': schedule.room_ko, 'type': schedule.get_type_display()} for schedule in lecture.classtime_set.all()],
			'remarks': u'영어강의' if lecture.is_english else u'',
			'examtime': {'day': exam.day, 'start': exam.get_begin_numeric(), 'end': exam.get_end_numeric()} if exam != None else None,
		}
		all.append(item)
	if conv_to_json:
		io = StringIO()
		if settings.DEBUG:
			json.dump(all, io, ensure_ascii=False, indent=4)
		else:
			json.dump(all, io, ensure_ascii=False, sort_keys=False, separators=(',',':'))
		return io.getvalue()
	else:
		return all

