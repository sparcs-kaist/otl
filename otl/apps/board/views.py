# encoding: utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from otl.apps.board import arara

NUM_PER_PAGE = 20

# 아라 게시판을 불러오는 경우의 핸들러
@login_required
def list_ara(request):

	if not arara.login():
		return HttpResponse('Cannot connect to arara')

	server = arara.get_server()
	session = arara.get_session_key()

	page_no = int(request.GET.get('page', 1))
	article_result = server.article_manager.article_list(session, 'Lecture', page_no, NUM_PER_PAGE)
	article_list = article_result.hit

	for article in article_list:
		if article.deleted:
			article.title = '-- Deleted --'
			article.author_username = ''
	
	# TODO: pagination
	
	return render_to_response('board/index_ara.html', {
		'section': 'board',
		'article_list': article_list,
	}, context_instance=RequestContext(request))

# 자체 게시판을 구현할 경우의 핸들러 (현재는 사용되지 않음)
def index(request):
	return render_to_response('board/index.html', {
		'section': 'board',
	}, context_instance=RequestContext(request))
