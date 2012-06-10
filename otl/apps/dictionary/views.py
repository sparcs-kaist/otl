# -*- coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.html import strip_tags, escape
from otl.apps.favorites.models import CourseLink
from otl.apps.common import *
from otl.utils.decorators import login_required_ajax
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture
from otl.apps.dictionary.models import *

from django import template
template.add_to_builtins('django.templatetags.i18n')

from django.utils.translation import ugettext
import datetime

def index(request):
    departments = Department.objects.all()
    return render_to_response('dictionary/index.html', {
        'section' : 'dictionary',
        'title' : ugettext(u'과목 사전'),
        'departments' : departments
    }, context_instance=RequestContext(request))

def department(request, department_id):
    dept = Department.objects.get(id=department_id)
    courses = Course.objects.filter(department=dept)
    return render_to_response('dictionary/department.html', {
        'section' : 'dictionary',
        'title' : ugettext(u'과목 사전'),
        'dept' : dept,
        'courses' : courses }, context_instance=RequestContext(request))

def search(request):
    pass

def view(request, course_code):
    try:
        course = Course.objects.get(code=course_code)
        summary = Summary.objects.filter(course=course).orber_by('-written_datetime')
        if summary.count() > 0:
            recent_summary = summary[0]
        else:
            recent_summary = None
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST'
    except:
        return HttpResponseServerError()
    return render_to_response('dictionary/view.html', {
        'result' : result,
        'course' : course,
        'professors' : Professor.objects.filter(course=course).order_by('professor_name'),
        'summary' : recent_summary,
        'comments' : Comment.objects.filter(course=course).order_by('-written_datetime')
    }, context_instance=RequestContext(request))

def view_comment_by_professor(request):
    try:
        professor_id = int(request.GET.get('professor_id', -1))
        course_id = int(request.GET.get('course_id', -1))
        if professor_id < 0 or course_id < 0:
            raise ValidationError()
        professor = Professor.objects.get(professor_id=professor_id)
        course = Course.objects.get(id=course_id)
        lecture = Lecture.objects.filter(professor=professor, course=course) 
        if not lecture.count() == 1:
            raise ValidationError()
        comments = Comment.objects.filter(course=course, lecture=lecture)
        result = 'OK'
    except ValidationError:
        result = 'ERROR'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST'
    return HttpResponse(json.dumps({
        'result': result,
        'comments': _comments_to_output(comments)}, ensure_ascii=False, indent=4))

@login_required_ajax
def add_comment(request):
    try:
        lecture_id = int(request.POST.get('lecture_id', -1))
        if lecture_id >= 0:
            lecture = Lecture.objests.get(id=lecture_id)
            course = lecture.course
        else:
            lecture = None
            course_id = int(request.POST.get('course_id', -1))
            if course_id >= 0:
                course = Course.objects.get(id=course_id)
            else:
                raise ValidationError()
        comment = request.POST.get('comment', None)
        load = int(request.POST.get('load', -1))
        gain = int(request.POST.get('gain', -1))
        score = int(request.POST.get('gain', -1))
        writer = request.user

        if load < 0 or gain < 0 or score < 0:
            raise ValidationError()

        new_comment = Comment(course=course, lecture=lecture, writer=writer, comment=comment, load=load, score=score, gain=gain)
        new_comment.save()
        result = 'ADD'

    except ValidationError:
        return HttpResponseBadRequest()
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'comment': _comments_to_output([new_comment])}, ensure_ascii=False, indent=4))
            
@login_required_ajax
def delete_comment(request):
    try:
        user = request.user
        comment_id = int(request.POST.get('comment_id', -1))

        if comment_id < 0:
            raise ValidationError()
        comment = Comment.objects.get(pk=comment_id, writer=user)
        comment.delete()
        result = 'DELETE'
    except ObjectDoesNotExist:
        result = 'REMOVE_NOT_EXIST'
    except ValidationError:
        return HttpResponseBadReqeust()
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result}, ensure_ascii=False, indent=4)) # TODO: 삭제를 위해서는 무엇을 리턴해야 하는가?

@login_required
def like_comment(request, comment_id):
    return 

@login_required
def add_summary(request):
    try:
        content = request.POST.get('content', None)
        course_id = int(request.POST.get('course_id', -1))
        course = Course.objects.get(id=course_id)
        if content == None or course_id < 0:
            raise ValidationError()
        writer = request.user
        written_datetime = datetime.now()
        new_summary = Summary(summary=content, writer=writer, written_datetime=writte_datetime, course=course)
        result = 'OK'
    except ValidationError:
        return HttpResponseBadReqeust()
    except:
        return HttpResponseServerError()
    
    return HttpResponse(json.dumps({
        'result': result,
        'summary': _summary_to_output([new_summary])}, ensure_ascii=False, indent=4))

def _comments_to_output(comments):
    all = []
    if not isinstance(comments, list):
        comments = comments.select_related()
    for comment in comments:
        writer = comment.writer
        item = {
            'course_id': comment.course.id,
            'lecture_id': comment.lecture.id,
            'writer_id': writer.id,
            'writer_nickname': writer.nickname,
            'written_datetime': comment.written_datetime,
            'content': comment.comment,
            'score': comment.score,
            'gain': comment.gain,
            'like': comment.like
        }
        all.append(item)
    return all

def _summary_to_output(summaries):
    all = []
    if not isintance(summaries, list):
        summaries = summaries.select_related()
    for summary in summaries:
        item = {
            'summary': summary.summary,
            'writer_id': summary.writer.id,
            'written_datetime': summary.written_datetime,
            'course_id': summary.course.id
            }
    return item

def _get_lecture_by_course(course):
    return
