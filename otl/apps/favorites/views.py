# encoding: utf8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from otl.apps.favorites.models import CourseLink
from otl.apps.common import *
import time

NUM_PER_PAGE = 10

def index(request):
	if request.user.is_authenticated():
		favorite_list = CourseLink.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, favored_by__exact=request.user)
	else:
		favorite_list = None
	
	page = request.GET.get('page', 1)
	courselink_pages = Paginator(CourseLink.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER).order_by('-written'), NUM_PER_PAGE)
	current_page = courselink_pages.page(page)
	# TODO: 나중에 영문 과목명과 한글 과목명 처리는 어떻게?

	return render_to_response('favorites/index.html', {
		'section': 'favorites',
		'favorite_list': favorite_list,
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
	}, context_instance=RequestContext(request))

def search(request):
	if request.user.is_authenticated():
		favorite_list = CourseLink.objects.filter(favored_by__exact=request.user)
	else:
		favorite_list = None
	page = request.GET.get('page', 1)
	courselink_pages = Paginator(CourseLink.objects.all().order_by('-written'), NUM_PER_PAGE)
	current_page = courselink_pages.page(page)

	search_page = request.GET.get('search-page',1)
	search_code = request.GET.get('query')
	search_list = Paginator(CourseLink.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, course_code__exact = search_code).order_by('-year','-semester','favored_count'), NUM_PER_PAGE)
	current_search_page = search_list.page(search_page)

	return render_to_response('favorites/index.html', {
		'section': 'favorites',
		'favorite_list': favorite_list,
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
		'search_list': search_list.object_list,
		'search_page': current_search_page,
	}, context_instance=RequestContext(request))
	
def add(request, course_id):
	if request.user.is_authenticated():
		course_selected = CourseLink.objects.get( id__exact = course_id )
		user = request.user
		count = course_selected.favored_count
		course_selected.favored_by.add( user )
		CourseLink.objects.filter(id__exact = course_id).update(favored_count = count + 1)

		favorite_list = CourseLink.objects.filter(favored_by__exact=request.user)
	else:
		favorites_list = None

	page = request.GET.get('page', 1)
	courselink_pages = Paginator(CourseLink.objects.all().order_by('-written'), NUM_PER_PAGE)
	current_page = courselink_pages.page(page)

	return render_to_response('favorites/index.html', {
		'section': 'favorites',
		'favorite_list': favorite_list,
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
	}, context_instance=RequestContext(request))

def create(request):
	new_code = request.GET.get('code')
	new_name = request.GET.get('name')
	new_year = request.GET.get('year')
	new_semester = request.GET.get('semester')
	new_url = request.GET.get('url')
	new_writer = request.user
	new_written = time.strftime('%Y-%m-%d %H:%M:%S')
	print(new_written)
	new_course_link = CourseLink.objects.create(course_code = new_code, course_name = new_name, year = new_year, semester = new_semester, url = new_url, writer = new_writer, written = new_written , favored_count = 0)
	
	page = request.GET.get('page',1)
	new_courselink_pages = Paginator(CourseLink.objects.all().order_by('-written'), NUM_PER_PAGE)
	current_page = new_courselink_pages.page(page)

	return render_to_response('favorites/index.html', {
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
	}, context_instance=RequestContext(request))

def delete(request, course_id):
	user = request.user
	delete_course = CourseLink.objects.get(id__exact = course_id)
	count = delete_course.favored_count
	delete_course.favored_by.remove(user)
	CourseLink.objects.filter(id__exact = course_id).update(favored_count = count - 1)
	favorite_list = CourseLink.objects.filter(favored_by__exact=request.user)

	return render_to_response('favorites/index.html', {
		'favorite_list': favorite_list,
	}, context_instance=RequestContext(request))


