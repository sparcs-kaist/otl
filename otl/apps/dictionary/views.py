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
    course = None
    if Course.objects.filter(code=course_code).count() == 0:
        lecture = Lecture.objects.get(code=course_code)
        course = Course.objects.create(\
            code = course_code,\
            department = lecture.department,\
            title = lecture.title,\
            title_en = lecture.title_en,\
            type = lecture.type,\
            type_en = lecture.type_en,\
            audience = lecture.audience,\
            credit = lecture.credit,\
            num_classes = lecture.num_classes,\
            num_labs = lecture.num_labs,\
            credit_au = lecture.credit_au,\
            limit = lecture.limit,\
            is_english = lecture.is_english,\
            deleted = lecture.deleted,\
            summary = ''
        )
        for lecture in Lecture.objects.filter(code=course_code):
            course.lectures.add(lecture)
        course.save()
    else:
        course = Course.objects.get(code=course_code)
    comments = Comment.objects.filter(course=course)
    return render_to_response('dictionary/view.html', {
        'section' : 'dictionary',
        'title' : ugettext(u'과목 사전'),
        'course' : course,
        'comments' : comments
    }, context_instance=RequestContext(request))

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
        'comment': _comment_to_output(new_comment)}))
            
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
        'result': result})) # TODO: 삭제를 위해서는 무엇을 리턴해야 하는가?

@login_required
def like_comment(request, comment_id):
    return 

@login_required
def add_summary(request, course_id):
    return

def _comment_to_output(comment):
    return
