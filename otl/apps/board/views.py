# -*- coding: utf-8
# Some codes are taken from warara, http://project.sparcs.org/arara/browser/trunk/warara/board/views.py
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from otl.apps.board import arara
from datetime import datetime
import re, math

NUM_PER_PAGE = 20
PAGES_PER_PAGEGROUP = 10
RX_URL = re.compile(r"(?#Protocol)(?:(?:ht|f)tp(?:s?)\:\/\/|~/|/)?(?#Username:Password)(?:\w+:\w+@)?(?#Subdomains)(?:(?:[-\w]+\.)+(?#TopLevelDomains)(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2}))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?[ ]*")

# 아라 게시판을 불러오는 경우의 핸들러
@login_required
def list_ara(request):
    if not arara.login():
        return HttpResponseServerError('Cannot connect to arara')
    server = arara.get_server()
    session = arara.get_session_key()

    try:
        page_no = int(request.GET.get('page', 1))
        page_range_no = math.ceil(float(page_no) / PAGES_PER_PAGEGROUP)
    except:
        return HttpResponseBadRequest()

    try:
        article_result = server.article_manager.article_list(session, 'Lecture', page_no, NUM_PER_PAGE)
    except:
        response = render_to_response('500.html', {'msg': u'아라 서버 접속이 원활하지 않습니다.'})
        response.status_code = 500
        return response
    article_list = article_result.hit

    # Pre-conversion
    for article in article_list:
        if article.deleted:
            article.title = '-- Deleted --'
            article.author_username = ''
            article.author_nickname = ''
        article.date = datetime.fromtimestamp(article.date)
    
    # Pagination with page groups containing 10 pages per group
    page_groups = Paginator([x+1 for x in xrange(article_result.last_page)], PAGES_PER_PAGEGROUP)
    pages = {}
    if page_groups.page(page_range_no).has_next():
        pages['next_page_group'] = page_groups.page(page_groups.page(page_range_no).next_page_number()).start_index()
    if page_groups.page(page_range_no).has_previous():
        pages['prev_page_group'] = page_groups.page(page_groups.page(page_range_no).previous_page_number()).end_index()
    pages['current_page_indices'] = page_groups.page(page_range_no).object_list
    
    return render_to_response('board/index_ara.html', {
        'section': 'board',
        'title': u'과목 Q&A',
        'article_list': article_list,
        'page_no': page_no,
        'pages': pages,
    }, context_instance=RequestContext(request))

def read_ara(request, id):
    if not arara.login():
        return HttpResponseServerError('Sorry, we could not connect to arara. Please check http://ara.kaist.ac.kr instead.')
    server = arara.get_server()
    session = arara.get_session_key()

    # 아래의 article_list는 댓글까지 모두 포함하고 있음.
    article_list = server.article_manager.read(session, 'Lecture', int(id))
    for article in article_list:
        if article.deleted:
            article.title = '-- Deleted --'
            article.content = '-- Deleted --'
            article.author_username = ''
            article.author_nickname = ''
        if article.depth > 12:
            article.depth = 12
        article.date = datetime.fromtimestamp(article.date)
        article.content = _render_ara_content(article.content.decode('utf-8'))

    page_no = int(request.GET.get('page', 1))
    return render_to_response('board/read_ara.html', {
        'section': 'board',
        'title': u'과목 Q&A - %s' % article_list[0].title.decode('utf-8'),
        'article_list': article_list,
        'page_no': page_no,
    }, context_instance=RequestContext(request))

# 자체 게시판을 구현할 경우의 핸들러 (현재는 사용되지 않음)
def index(request):
    return render_to_response('board/index.html', {
        'section': 'board',
    }, context_instance=RequestContext(request))


# -- Private functions --

def _render_ara_content(content):
    content = content.replace(u"<", u"&lt;").replace(u">", u"&gt;")
    urls_set = set(RX_URL.findall(content))
    for url in urls_set:
        tagged_url = u'<a href="' + url + '">' + url + u'</a>'
        content = content.replace(url, tagged_url)
    return content
