# encoding: utf8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from otl.apps.favorites.models import CourseLink
import time

SEMESTER_NAMES = {
	1: u'ë´?,
	2: u'?¬ë¦„',
	3: u'ê°€??,
	4: u'ê²¨ìš¸',
}
NUM_PER_PAGE = 10

def index(request):
	if request.user.is_authenticated():
		favorite_list = CourseLink.objects.filter(favored_by__exact=request.user)
	else:
		favorite_list = None
	
	page = request.GET.get('page', 1)
	courselink_pages = Paginator(CourseLink.objects.all().order_by('-written'), NUM_PER_PAGE)
	current_page = courselink_pages.page(page)
	# TODO: ?˜ì¤‘???ë¬¸ ê³¼ëª©ëª…ê³¼ ?œê? ê³¼ëª©ëª?ì²˜ë¦¬???´ë–»ê²?

	return render_to_response('favorites/index.html', {
		'section': 'favorites',
		'current_year': 2009, # TODO: ê³µí†µ?ìœ¼ë¡??¬ìš©?????ˆê²Œ middlewareë¡?ì²˜ë¦¬?˜ëŠ” ê²?ì¢‹ì„ ??
		'current_semester': SEMESTER_NAMES[1],
		'favorite_list': favorite_list,
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
	}, context_instance=RequestContext(request))

def search(request):
	search_page = request.GET.get('search-page',1)
	search_code = request.GET.get('query')
	search_list = Paginator(CourseLink.objects.filter(course_code__exact = search_code).order_by('-year','-semester','favored_count'), NUM_PER_PAGE)
	current_search_page = search_list.page(search_page)

	return render_to_response('favorites/index.html', {
		'search_list': search_list.object_list,
		'search_page': current_search_page,
	}, context_instance=RequestContext(request))
	
def add(request, course_id):
	if request.user.is_authenticated():
		course_selected = CourseLink.objects.get( id__exact = course_id )
		user = request.user
		course_selected.favored_by.add( user )

		favorite_list = CourseLink.objects.filter(favored_by__exact=request.user)
	else:
		favorites_list = None

	page = request.GET.get('page', 1)
	courselink_pages = Paginator(CourseLink.objects.all().order_by('-written'), NUM_PER_PAGE)
	current_page = courselink_pages.page(page)

	return render_to_response('favorites/index.html', {
		'section': 'favorites',
		'current_year': 2009,
		'current_semester': SEMESTER_NAMES[1],
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
	new_written = time.ctime()

	new_course_link = CourseLink.objects.create(course_code = new_code, course_name = new_name, year = new_year, semester = new_semester, url = new_url, writer = new_writer, written = new_written)
	
	page = request.GET.get('page',1)
	new_courselink_pages = Paginator(CourseLink.objects.all().order_by('-written'), NUM_PER_PAGE)
	current_page = new_courselink_pages.page(page)

	return render_to_response('favorites/index.html', {
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
	}, context_instance=RequestContext(request))

def delete(request, course_id):
	user = request.user
	delete_course = CourseLink.objects.get(id = course_id)
	delete_course.favored_by.remove(user)
	favorite_list = CourseLink.objects.filter(favored_by__exact=request.user)

	return render_to_response('favorites/index.html', {
		'favorite_list': favorite_list,
	}, context_instance=RequestContext(request))


