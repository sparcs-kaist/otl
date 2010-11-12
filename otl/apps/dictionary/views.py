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
    comments = CourseComment.objects.filter(course=course)
    return render_to_response('dictionary/view.html', {
	    'section' : 'dictionary',
    	'title' : ugettext(u'과목 사전'),
    	'course' : course,
        'comments' : comments
    }, context_instance=RequestContext(request))

@login_required
def add_comment(request, course_id):
    new_course = Course.objects.get(id=course_id)
    new_lecture = Lecture.objects.get(id=int(request.POST['lecture_id']))
    new_comment = escape(strip_tags(request.POST['comment']))
    if request.POST['load'] == 'True':
        new_load = True
    elif request.POST['load'] == 'False':
        new_load = False
    else:
        new_load = None
    if request.POST['score'] == 'True':
        new_score = True
    elif request.POST['score'] == 'False':
        new_score = False
    else:
        new_score = None
    if request.POST['gain'] == 'True':
        new_gain = True
    elif request.POST['gain'] == 'False':
        new_gain = False
    else:
        new_gain = None

    comment = CourseComment.objects.create(\
        writer = request.user,\
        course = new_course,\
        lecture = new_lecture,\
        comment = new_comment,\
        load = new_load,\
        score = new_score,\
        gain = new_gain\
    )
    comment.save()
    return HttpResponseRedirect('/dictionary/view/' + new_course.code)

@login_required
def delete_comment(request, comment_id):
    comment = CourseComment.objects.get(id=comment_id)
    if comment.User == request.user:
        comment.delete()
    return HttpResponseRedirect('/dictionary/view/' + comment.course.code)


