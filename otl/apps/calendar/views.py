# encoding: utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.conf import settings
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required
from otl.apps.calendar.forms import ScheduleForm
from otl.apps.calendar.models import Calendar, Schedule
from otl.utils.decorators import login_required_ajax
from otl.utils import render_as_json

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
	return render_as_json(result)

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
	return render_as_json(result)

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
			"description": string or null,
			"date": "YYYY-MM-DD",
			"time_start": integer representing minutes from 00:00,
			"time_end": integer representing minutes from 00:00
		},
		...
	]
	"""

	items = Schedule.objects.filter(date__gte=date_start, date__lte=date_end)
	result = []
	for item in items:
		result.append({
			'id': item.id,
			'calendar': item.belongs_to.id,
			'summary': item.summary,
			'location': item.location,
			'description': item.description,
			'date': item.date.strftime('%Y-%m-%d'),
			'time_start': item.time_start.hour * 60 + item.time_start.minute,
			'time_end': item.time_end.hour * 60 + item.time_end.minute,
		})
	return render_as_json(result)

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
	return render_as_json(result)

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
	return render_as_json(result)

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
	return render_as_json(result)

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
	return render_as_json(result)

@login_required
def search_schedule(request):
	pass

