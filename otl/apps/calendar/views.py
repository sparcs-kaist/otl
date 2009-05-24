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
def add_shcedule(request):
	"""
	Adds a schedule item.
	Currently does not support repeated schedules.

	Request: use GET parameters
	- type : "repeated" | "single"
	- summary : user string (max 120 chars)
	- location : user string (max 120 chars, may be blank)
	- description : user string (long, may be blank)
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
def delete_schedule(request):
	"""
	Delete a schedule item.

	Request: use GET parameters
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

