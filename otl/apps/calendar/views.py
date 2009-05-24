# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.decorators import login_required
from otl.utils.decorators import login_required_ajax

def index(request):
	if settings.SERVICE_STATUS == 'beta':
		return render_to_response('calendar/beta.html', {
			'section': 'calendar',
			'title': u'일정관리',
		}, context_instance=RequestContext(request))
	else:
		return render_to_response('calendar/index.html', {
			'section': 'calendar',
			'title': u'일정관리',
		}, context_instance=RequestContext(request))

@login_required_ajax
def list_calendar(request):
	"""
	Lists the calendars.

	Request: None
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

	# TODO: implement

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

	# TODO: implement

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

	# TODO: implement

@login_required_ajax
def add_shcedule(request):
	"""
	Adds a schedule item.
	Currently does not support repeated schedules.

	Request: use POST parameters
	- type : "repeated" | "single"
	- summary : user string (max 120 chars)
	- location : user string (max 120 chars, optional)
	- description : user string (long, optional)
	- date : "YYYY-MM-DD"
	- time_start : integer representing minutes from 00:00
	- time_end : integer representing minutes from 00:00

	Response: use JSON string
	{
		"result": "OK" | "FAILED",
		"id": integer id of the created item,
	}
	"""

	# TODO: implement

@login_required_ajax
def modify_schedule(request):
	"""
	Modifies a schedule item.

	Request: use POST parameters
	- summary
	- location
	- description
	- date
	- time_start
	- time_end

	Response: use JSON string
	{
		"result": "OK" | "NOT_FOUND" | "FAILED"
	}
	"""

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

	# TODO: implement

@login_required
def search_schedule(request):
	pass

