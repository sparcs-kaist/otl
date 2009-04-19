# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.db.models import Q

from otl.apps.groups.models import GroupBoard
from otl.apps.groups.models import GroupArticle
from otl.apps.common import *
import time
import md5

NUM_PER_PAGE = 10
RECENTLY_PER_PAGE = 3

def index(request):
	if request.user.is_authenticated():
		group_list = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, group_in__exact=request.user)
	else:
		group_list = None
	
	group_pages = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER).order_by('-made')[0:RECENTLY_PER_PAGE]
	# TODO: 나중에 영문 과목명과 한글 과목명 처리는 어떻게?

	return render_to_response('groups/index.html', {
		'section': 'groups',
		'group_list': group_list,
		'recently_added_list': group_pages,
	}, context_instance=RequestContext(request))

def create(request):
	if request.user.is_authenticated():
		new_code = request.POST.get('code')
		new_course_name = request.POST.get('cname')
		new_group_name = request.POST.get('gname')
		new_pw = request.POST.get('passwd')
		new_comment = request.POST.get('comment')
		new_year = settings.CURRENT_YEAR
		new_semester = settings.CURRENT_SEMESTER
		new_maker = request.user
		new_made = time.strftime('%Y-%m-%d %H:%M:%S')
		pw = md5.new(new_pw).hexdigest()
		print(pw)
		new_group = GroupBoard.objects.create(course_code = new_code, course_name = new_course_name, group_name = new_group_name, passwd = pw, comment = new_comment, year = new_year, semester = new_semester, maker = new_maker, made = new_made)
		new_group.group_in.add(new_maker);
	else:
		group_list=None

	return HttpResponseRedirect('/groups/');

def join(request, group_id):
	if request.user.is_authenticated():
		user = request.user
		group_selected = GroupBoard.objects.get( id__exact = group_id ).group_in.add( user )
	else:
		group_list=None

	return HttpResponseRedirect('/groups/');

def withdraw(request, group_id):
	if request.user.is_authenticated():
		user = request.user
		GroupBoard.objects.get(id__exact = group_id).group_in.remove(user)
	else:
		group_list = None
	return HttpResponseRedirect('/groups/');

def search(request):
	if request.user.is_authenticated():
		group_list = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, group_in__exact=request.user)
	else:
		favorite_list = None
	
	group_pages = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER).order_by('-made')[0:RECENTLY_PER_PAGE]
	search_code = request.GET.get('query')
	search_list = Paginator(GroupBoard.objects.filter(Q(year=settings.CURRENT_YEAR),Q(semester=settings.CURRENT_SEMESTER), Q(course_code__icontains = search_code)|Q(course_name__icontains = search_code)|Q(group_name__icontains = search_code)).order_by('-made'),NUM_PER_PAGE)
	search_page = request.GET.get('search-page',1)
	current_search_page = search_list.page(search_page)
	return render_to_response('groups/index.html', {
		'section': 'groups',
		'search_code': search_code,
		'search_page': current_search_page,
		'search_list': current_search_page.object_list,
		'group_list': group_list,
		'recently_added_list': group_pages,
	}, context_instance=RequestContext(request))
		
def morelist(request):
	if request.user.is_authenticated():
		group_list = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, group_in__exact=request.user)
	else:
		group_list = None
	page = request.GET.get('page',1)
	groupboard_pages = Paginator(GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER).order_by('-made'), NUM_PER_PAGE)
	current_page = groupboard_pages.page(page)

	return render_to_response('groups/index.html', {
		'section': 'groups',
		'group_list': group_list,
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
	}, context_instance=RequestContext(request))

def list(request, group_id):
	is_in_group = 0
	page = None
	article_pages = None
	current_page = None
	if request.user.is_authenticated():
		user = request.user
		#group_selected = GroupBoard.objects.get( id__exact = group_id)
		group =user.group_set.get(id__exact = group_id) 
		if group:
			is_in_group = 1
			page = request.GET.get('page',1)
			article_pages = Paginator(GroupArticle.objects.filter(group__id__exact = group_id).order_by('-written'), NUM_PER_PAGE)
			current_page = article_pages.page(page)

	return render_to_response('groups/list.html', {
		'section': 'groups',
		'current_group': group,
		'article_list': current_page.object_list,
		'article_page': current_page,
		'is_in_group': is_in_group,
	}, context_instance=RequestContext(request))

def write(request, group_id):
	if request.user.is_authenticated():
		user=request.user
		current_group = user.group_set.get(id__exact = group_id)
		new_written = time.strftime('%Y-%m-%d %H:%M:%S')
		if current_group:
			new_tag = request.POST.get('article')
			GroupArticle.objects.create(group = current_group, tag = new_tag, writer = user, written = new_written)

	return HttpResponseRedirect('/groups/list/'+group_id);



