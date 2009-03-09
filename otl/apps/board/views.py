# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext

# 아라 게시판을 불러오는 경우의 핸들러
def index_ara(request):
	return render_to_response('board/index_ara.html', {
		'section': 'board',
	}, context_instance=RequestContext(request))

# 자체 게시판을 구현할 경우의 핸들러 (현재는 사용되지 않음)
def index(request):
	return render_to_response('board/index.html', {
		'section': 'board',
	}, context_instance=RequestContext(request))
