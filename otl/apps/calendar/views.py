# encoding: utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.conf import settings
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from otl.apps.calendar.forms import ScheduleForm, ScheduleListForm
from otl.apps.calendar.models import Calendar, Schedule, fetch_assignments, fetch_taking_courses, get_system_calendar
from otl.apps.timetable.models import Lecture, ClassTime
from otl.utils.decorators import login_required_ajax
from otl.utils import response_as_json
from datetime import *

def index(request):
	if settings.SERVICE_STATUS == 'beta':
		return render_to_response('calendar/beta.html', {
			'section': 'calendar',
			'title': u'일정관리',
		}, context_instance=RequestContext(request))
	else:
		f = ScheduleForm()
		return render_to_response('calendar/index.html', {
			'section': 'calendar',
			'title': u'일정관리',
			'schedule_form': f,
		}, context_instance=RequestContext(request))

@login_required_ajax
def list_calendar(request):
	"""
	Lists the calendars.

	Request: None; method is GET

	Response: use JSON string
	[
		{
			"id": integer id of a calendar,
			"title": string,
			"color": integer index of predefined colors,
			"enabeld": boolean
		},
		...
	]
	"""

	items = Calendar.objects.filter(owner=request.user)	
	result = []
	for item in items:
		result.append({
			'id': item.id,
			'title': item.title,
			'color': item.color,
			'enabled': item.enabled,
		})
	return response_as_json(request, result)

@login_required_ajax
def modify_calendar(request):
	"""
	Modifies the propreties of the indicated calendar.

	Request: use POST parameters
	- id : integer id of a calendar
	- color : integer index of predefined colors (1~10, optional)
	- title : user string (max 60 chars, optional)
	- enabled : true or false (optional)

	Response: use JSON string
	{
		"result": "OK" | "NOT_FOUND" | "FAILED"
	}
	"""
	if request.method == 'POST':
		try:
			item = Calendar.objects.get(id__exact=id)
			if request.POST.has_key('color'):
				item.color = int(request.POST['color'])
			if request.POST.has_key('title'):
				item.title = request.POST['title']
			if request.POST.has_key('enabled'):
				item.enabled = bool(request.POST['enabled'])
			item.save()
			result = {'result':'OK'}
		except Calendar.DoesNotExist:
			result = {'result':'NOT_FOUND'}
		except TypeError, ValueError:
			result = {'result':'FAILED'}
	else:
		return HttpResponseBadRequest('Should be called with POST method')
	return response_as_json(request, result)

@login_required_ajax
def list_schedule(request):
	"""
	Lists schedule items within a specific date range.

	Request: use GET parameters
	- date_start : "YYYY-MM-DD"
	- date_end : "YYYY-MM-DD"
	
	Response: use JSON string
	[
		{
			"id": integer id of an item,
			"calendar": integer id of the calendar to which this belongs,
			"summary": string,
			"location": string or null,
			"range": integer; 0 (일일), 1 (종일)
			"description": string or null,
			"date": "YYYY-MM-DD",
			"time_start": integer representing minutes from 00:00,
			"time_end": integer representing minutes from 00:00
		},
		...
	]
	"""

	f = ScheduleListForm(request.GET)
	print 'processing list_schedule()'
	if f.is_valid():
		
		# TODO: 나중에 일주일보다 큰 간격으로 요청해올 경우 시간표 schedule 처리를 loop로 돌아야 함.
		date_start = f.cleaned_data['date_start']
		date_end = f.cleaned_data['date_end']
		if date_end - date_start > timedelta(days=7, hours=0, minutes=0):
			return HttpResponseBadRequest('Unimplemented size of date difference.')

		# Auto-update schedules from timetables
		current_week_start = date_start - timedelta(days = (date_start.toordinal() % 7), hours=0, minutes=0)
		timetable_calendar = get_system_calendar(request.user, 'timetable')
		lectures = fetch_taking_courses(int(request.user.userprofile.student_id))
		for lecture in lectures:
			class_times = lecture.classtime_set.all()
			print 'Taking course : %s' % lecture.code
			for class_time in class_times:
				# TODO: 과목시간표에 대한 30분 단위 올림 처리
				class_date = current_week_start + timedelta(days=class_time.day + 1, hours=0, minutes=0)
				if class_date >= date_start and class_date <= date_end:
					try:
						Schedule.objects.get(summary__startswith=lecture.title, date=class_date, begin=class_time.begin, end=class_time.end)
					except Schedule.DoesNotExist:
						s = Schedule()
						s.summary = u'%s%s' % (lecture.title, u' (실험)' if class_time.type == 'e' else u'')
						s.belongs_to = timetable_calendar
						s.one_of = None
						s.location = class_time.get_location()
						s.range = 0 # 일일 일정
						s.date = class_date
						s.begin = class_time.begin
						s.end = class_time.end
						s.save()

		result = []
		items = Schedule.objects.filter(date__gte=date_start, date__lte=date_end)
		for item in items:
			result.append({
				'id': item.id,
				'calendar': item.belongs_to.id,
				'summary': item.summary,
				'location': item.location,
				'range': item.range,
				'description': item.description,
				'date': item.date.strftime('%Y-%m-%d'),
				'time_start': item.begin.hour * 60 + item.begin.minute,
				'time_end': item.end.hour * 60 + item.end.minute,
			})
		return response_as_json(request, result)
	else:
		return HttpResponseBadRequest('Invalid parameters (date_start, date_end)')

@login_required_ajax
def get_schedule(request):
	"""
	Get a single schedule item.

	Request: use GET parameters
	- id : integer id of an item

	Response: use JSON string
	{
		"result":"OK" | "NOT_FOUND" | "FAILED",
		"item": {
			(same as above)
		}
	}
	"""

	try:
		item = Schedule.objects.get(id__exact=request.POST['id'])
		result = {'result':'OK', 'item':{
			'id': item.id,
			'calendar': item.belongs_to.id,
			'summary': item.summary,
			'location': item.location,
			'description': item.description,
			'date': item.date.strftime('%Y-%m-%d'),
			'time_start': item.time_start.hour * 60 + item.time_start.minute,
			'time_end': item.time_end.hour * 60 + item.time_end.minute,
		}}
	except Schedule.DoesNotExist:
		result = {'result':'NOT_FOUND'}
	except (KeyError, TypeError, ValueError):
		result = {'result':'FAILED'}
	return response_as_json(request, result)

@login_required_ajax
def add_schedule(request):
	"""
	Adds a schedule item.
	Currently does not support repeated schedules.

	Request: use POST parameters
	- type : "repeated" | "single"
	- calendar : integer id of a calendar which will include this item
	- summary : user string (max 120 chars)
	- location : user string (max 120 chars, optional)
	- range : integer; 0 (일일), 1 (종일)
	- description : user string (long, optional)
	- date : "YYYY-MM-DD"
	- time_start : integer representing minutes from 00:00
	- time_end : integer representing minutes from 00:00

	You should refer ScheduleForm in forms.py.
	It will validate the input from the web browser.

	Response: use JSON string
	{
		"result": "OK" | "NOT_FOUND" | "FAILED",
		"id": integer id of the created item,
	}
	"""

	if request.method == 'POST':
		try:
			item = Schedule()
			f = ScheduleForm(request.POST)
			if f.valid():
				item.summary = f.cleaned_data['summary']
				item.location = f.cleaned_data['location']
				item.description = f.cleaned_data['description']
				item.range = f.cleaned_data['range']
				item.date = f.cleaned_data['date']
				item.time_start = f.cleaned_data['time_start']
				item.time_end = f.cleaned_data['time_end']
				item.belgons_to = Calendar.objects.get(id__exact=f.cleaned_data['id'])
				item.save()
				result = {'result':'OK'}
			else:
				result = {'result':'FAILED'}
		except Calendar.DoesNotExist:
			result = {'result':'NOT_FOUND'}
		except (KeyError, TypeError, ValueError):
			result = {'result':'FAILED'}
	else:
		return HttpResponseBadRequest('Should be called with POST method.')
	return response_as_json(request, result)

@login_required_ajax
def modify_schedule(request):
	"""
	Modifies a schedule item.

	Request: use POST parameters
	- id : integer id of an item
	- summary : user string
	- location : user string (optional)
	- description : user string (optional)
	- date : "YYYY-MM-DD" (optional)
	- time_start : integer representing minutes from 00:00 (optional)
	- time_end : integer representing minutes from 00:00 (optional)

	You should refer ScheduleModifyForm in forms.py.
	The request should be filled with all necessary fields.
	(Not only the changed fields)

	Response: use JSON string
	{
		"result": "OK" | "NOT_FOUND" | "FAILED"
	}
	"""
	if request.method == 'POST':
		try:
			f = ScheduleModifyForm(request.POST)
			if f.is_valid():
				item = Schedule.objects.get(id__exact=f.cleaned_data['id'])
				item.summary = f.cleaned_data['summary']
				item.location = f.cleaned_data['location']
				item.description = f.cleaned_data['description']
				item.date = f.cleaned_data['date']
				item.time_start = f.cleaned_data['time_start']
				item.time_end = f.cleaned_data['time_end']
				item.belgons_to = Calendar.objects.get(id__exact=f.cleaned_data['id'])
				item.save()
				result = {'result':'OK'}
			else:
				result = {'result':'FAILED'}
		except Schedule.DoesNotExist:
			result = {'result':'NOT_FOUND'}
		except KeyError, ValueError:
			result = {'result':'FAILED'}
	else:
		return HttpResponseBadRequest('Should be called with POST method.')
	return response_as_json(request, result)

@login_required_ajax
def delete_schedule(request):
	"""
	Delete a schedule item.

	Request: use POST parameters
	- id : integer id of an item

	Response: use JSON string
	{
		"result": "OK" | "NOT_FOUND" | "FAILED"
	}
	"""

	if request.method == 'POST':
		try:
			Schedule.objects.get(id=request.POST['id']).delete()
			result = {'result':'OK'}
		except Schedule.DoesNotExist:
			result = {'result':'NOT_FOUND'}
		except KeyError, ValueError:
			result = {'result':'FAILED'}
	else:
		return HttpResponseBadRequest('Should be called with POST method.')
	return response_as_json(request, result)

@login_required_ajax
def get_assignments(request):
	"""
	Retrieves the current user's assignments from Moodle.

	Request: None
	Response: use JSON string
	{
		"result": "OK" | "FAILED", // This handler may fail due to connection problems.
		"assignments": [
			{
				"course": string (2~3 alphabet + 3 digits),
				"name": string,
				"description": string,
				"due_date": "YYYY-MM-DD",
				"due_time": integer representing minutes from 00:00,
				"grade": integer
			},
			...
		]
	}
	"""

	try:
		items = fetch_assignments(int(request.user.userprofile.student_id))
		assignments = []
		for item in items:
			# item[5], item[6], item[8] was already converted to python datetime objects.
			t = item[5].time()
			assignments.append({
				'course': item[0],
				'name': item[1],
				'description': item[2],
				'due_date': item[5].date().strftime('%Y-%m-%d'),
				'due_time': t.hour * 60 + t.minute,
				'grade': item[7],
			})
		result = {
			'result': 'OK',
			'assignments': assignments,
		}
	except DatabaseError, e:
		result = {'result': 'FAILED', 'error': e.message, 'assignments': []}
	
	return response_as_json(request, result)

