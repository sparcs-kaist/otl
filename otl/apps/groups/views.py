# -*- coding: utf-8
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

    return render_to_response('groups/index.html', {
        'section': 'groups',
        'title': u'조모임',
        'group_list': group_list,
        'recently_added_list': group_pages,
    }, context_instance=RequestContext(request))

def create(request):
    if request.user.is_authenticated():
        if GroupBoard.objects.filter(maker__exact = request.user).count() < 11:
            new_group_name = request.POST.get('gname')
            new_pw = request.POST.get('passwd')
            new_comment = request.POST.get('comment')
            new_year = settings.CURRENT_YEAR
            new_semester = settings.CURRENT_SEMESTER
            new_maker = request.user
            new_made = time.strftime('%Y-%m-%d %H:%M:%S')
            pw = md5.new(new_pw).hexdigest()
            new_group = GroupBoard.objects.create(group_name = new_group_name, passwd = pw, comment = new_comment, year = new_year, semester = new_semester, maker = new_maker, made = new_made)
            new_group.group_in.add(new_maker);


    return HttpResponseRedirect('/groups/');

def join(request, group_id):
    if request.user.is_authenticated():
        user = request.user
        passwd = md5.new(request.POST.get("passwd")).hexdigest()
        group_selected = GroupBoard.objects.filter( id__exact = group_id, passwd__exact = passwd )
        if group_selected:
            group_selected[0].group_in.add(user)

    return HttpResponseRedirect('/groups/');

def withdraw(request, group_id):
    if request.user.is_authenticated():
        user = request.user
        GroupBoard.objects.get(id__exact = group_id).group_in.remove(user)

    return HttpResponseRedirect('/groups/');

def search(request):
    if request.user.is_authenticated():
        group_list = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, group_in__exact=request.user)
    else:
        group_list = None
    
    group_pages = GroupBoard.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER).order_by('-made')[0:RECENTLY_PER_PAGE]
    search_code = request.GET.get('query')
    search_list = Paginator(GroupBoard.objects.filter(Q(year=settings.CURRENT_YEAR),Q(semester=settings.CURRENT_SEMESTER), Q(comment__icontains = search_code)|Q(group_name__icontains = search_code)).order_by('-made'),NUM_PER_PAGE)
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
        'title': u'조모임',
        'group_list': group_list,
        'recently_added_list': current_page.object_list,
        'current_page': current_page,
    }, context_instance=RequestContext(request))

def list(request):
    if request.user.is_authenticated():
        group_id=request.GET.get('id')
        user = request.user
        group =user.group_set.filter(id__exact = group_id) 
        if group:
            page = request.GET.get('page',1)
            article_pages = Paginator(GroupArticle.objects.filter(group__id__exact = group_id).order_by('-written'), NUM_PER_PAGE)
            current_page = article_pages.page(page)
            return render_to_response('groups/list.html', {
                'section': 'groups',
                'title': u'조모임',
                'current_group': group[0],
                'article_list': current_page.object_list,
                'current_page': current_page,
                'group_id' : group_id,
            }, context_instance=RequestContext(request))

    return HttpResponseRedirect('/groups/');

def write(request, group_id):
    if request.user.is_authenticated():
        user=request.user
        current_group = user.group_set.get(id__exact = group_id)
        new_written = time.strftime('%Y-%m-%d %H:%M:%S')
        if current_group:
            new_tag = request.POST.get('article')
            GroupArticle.objects.create(group = current_group, tag = new_tag, writer = user, written = new_written)

    return HttpResponseRedirect('/groups/list/?id='+group_id);

def delete(request):
    if request.user.is_authenticated():
        group_id = request.GET.get('id')
        user = request.user
        article_id = request.GET.get('num')
        delete_article = GroupArticle.objects.filter(writer__exact = user, id__exact = article_id)
        if delete_article != None :
            delete_article.delete()

    return HttpResponseRedirect('/groups/list/?id='+group_id);

def modify(request):
    if request.user.is_authenticated():
        group_id = request.GET.get('id')
        user = request.user
        article_id = request.GET.get('num')
        new_article = request.POST.get('modify')
        GroupArticle.objects.filter(writer__exact = user, id__exact = article_id).update(tag = new_article)

    return HttpResponseRedirect('/groups/list/?id='+group_id);

def article_search(request):
    if request.user.is_authenticated():
        group_id=request.GET.get('id')
        user = request.user
        group = user.group_set.filter(id__exact = group_id)
        if group:
            page = request.GET.get('page',1)
            article_pages = Paginator(GroupArticle.objects.filter(group__id__exact = group_id).order_by('-written'), NUM_PER_PAGE)
            current_page = article_pages.page(page)
            if request.GET.get('query'):
                search_code = request.GET.get('query')
            else : 
                search_code = request.POST.get('query')
            search_list = Paginator(GroupArticle.objects.filter(Q(group__id__exact = group_id), (Q(writer__username__icontains = search_code)|Q(tag__icontains = search_code))).order_by('-written'),NUM_PER_PAGE)
            search_page = request.GET.get('search-page',1)
            current_search_page = search_list.page(search_page)
            return render_to_response('groups/list.html', {
                'section': 'groups',
                'title': u'조모임',
                'current_group': group[0],
                'article_list': current_page.object_list,
                'article_page': current_page,
                'search_code': search_code,
                'search_page': current_search_page,
                'search_list': current_search_page.object_list,
            }, context_instance=RequestContext(request))

            
    return HttpResponseRedirect('/groups/');
