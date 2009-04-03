# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from otl.apps.favorites.models import CourseLink

SEMESTER_NAMES = {
	1: u'봄',
	2: u'여름',
	3: u'가을',
	4: u'겨울',
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
	# TODO: 나중에 영문 과목명과 한글 과목명 처리는 어떻게?

	return render_to_response('favorites/index.html', {
		'section': 'favorites',
		'current_year': 2009, # TODO: 공통적으로 사용할 수 있게 middleware로 처리하는 게 좋을 듯.
		'current_semester': SEMESTER_NAMES[1],
		'favorite_list': favorite_list,
		'recently_added_list': current_page.object_list,
		'current_page': current_page,
	}, context_instance=RequestContext(request))
