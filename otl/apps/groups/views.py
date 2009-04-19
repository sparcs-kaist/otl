# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from otl.apps.groups.models import GroupBoard
from otl.apps.common import *
import time

NUM_PER_PAGE = 10
RECENTLY_PER_PAGE = 3

def index(request):
	if request.user.is_authenticated():
		group_list = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, group_in__exact=request.user)
	else:
		favorite_list = None
	
	group_pages = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER).order_by('-made')[0:RECENTLY_PER_PAGE]
	# TODO: 나중에 영문 과목명과 한글 과목명 처리는 어떻게?

	return render_to_response('groups/index.html', {
		'section': 'groups',
		'group_list': group_list,
		'recently_added_list': group_pages,
	}, context_instance=RequestContext(request))

def create(request):
	if request.user.is_authenticated():
		new_code = request.GET.get('code')
		new_course_name = request.GET.get('cname')
		new_group_name = request.GET.get('gname')
		new_year = request.GET.get('year')
		new_semester = request.GET.get('semester')
		new_maker = request.user
		new_made = time.strftime('%Y-%m-%d %H:%M:%S')
		new_group = GroupBoard.objects.create(course_code = new_code, course_name = new_course_name, group_name = new_group_name, year = new_year, semester = new_semester, maker = new_maker, made = new_made)
		new_group.group_in.add(new_maker);
	else:
		favorite_list=None

	return HttpResponseRedirect('/groups/');

