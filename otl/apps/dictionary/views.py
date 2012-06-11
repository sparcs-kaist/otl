# -*- coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.core.exceptions import *
from django.conf import settings
from django.contrib.auth.models import User
from django.http import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.html import strip_tags, escape
from django.utils import simplejson as json
from otl.apps.favorites.models import CourseLink
from otl.apps.common import *
from otl.utils import respond_as_attachment
from otl.utils.decorators import login_required_ajax
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture
from otl.apps.dictionary.models import *
from otl.apps.timetable.views import _lectures_to_output

from django import template
template.add_to_builtins('django.templatetags.i18n')

from django.utils.translation import ugettext
import datetime

def index(request):

    #Make the semester info to make users select the semester which they want to view.
    semester_info = []
    semester_info.append({'year' : settings.START_YEAR, 'semester' : settings.START_SEMESTER})
    if settings.START_SEMESTER == 1 and settings.NEXT_YEAR > settings.START_YEAR:
        semester_info.append({'year' : settings.START_YEAR, 'semester' : 3})
    for y in range(settings.START_YEAR+1,settings.NEXT_YEAR):
        semester_info.append({'year' : y, 'semester' : 1})
        semester_info.append({'year' : y, 'semester' : 3})
    if settings.NEXT_SEMESTER == 3 and settings.NEXT_YEAR > settings.START_YEAR:
        semester_info.append({'year' : settings.NEXT_YEAR, 'semester' : 1})

    # Read the current user's timetable.
    if request.user.is_authenticated():
        my_lectures = [_lectures_to_output(Lecture.objects.filter(year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER, timetable__user=request.user, timetable__table_id=id), False, request.session.get('django_language', 'ko')) for id in xrange(0,settings.NUMBER_OF_TABS)]
    else:
        my_lectures = [[], [], []]
    if settings.DEBUG:
        my_lectures_output = json.dumps(my_lectures, indent=4, ensure_ascii=False)
    else:
        my_lectures_output = json.dumps(my_lectures, ensure_ascii=False, sort_keys=False, separators=(',',':'))

    rank_list = [{'rank':0, 'ID':'noname', 'score':u'넘겨줘'}]*10
    monthly_rank_list = [{'rank':0, 'ID':'noname', 'score':u'넘겨줘'}]*10
    todo_comment_list = [{'semester':u'0000ㅁ학기', 'code':'XX000', 'lecture_name':'넘겨', 'prof':'넘겨', 'url':'/넘겨야할/주소/줘'}]*10
    return render_to_response('dictionary/index.html', {
        'section': 'dictionary',
        'title': ugettext(u'과목 사전'),
        'departments': Department.objects.filter(visible=True).order_by('name'),
        'my_lectures': my_lectures_output,
        'lang' : request.session.get('django_language', 'ko'),
        'semester_info' : semester_info,
        'username' : u'넘겨줘',
        'nickname' : u'넘겨줘',
        'studentno' : u'넘겨줘',
        'department' : u'넘겨줘',
        'score' : u'넘겨줘',
        'rank' : u'넘겨줘',
        'rank_list' : rank_list,
        'taken_credits' : u'넘겨줘',
        'taken_AU' : u'넘겨줘',
        'planned_credits' : u'넘겨줘',
        'planned_AU' : u'넘겨줘',
        'monthly_rank_list' : monthly_rank_list,
        'todo_comment_list' : todo_comment_list,
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
    try:
        q = {}
        for key, value in request.GET.iteritems():
            q[str(key)] = value

        output = _courses_to_output(_search(**q), True, request.session.get('django_language', 'ko'))
        return HttpResponse(output)
    except:
        return HttpResponseBadRequest()

def view(request, course_code):
    course = None
    recent_summary = None

    try:
        course = Course.objects.get(old_code=course_code)
        summary = Summary.objects.filter(course=course).order_by('-written_datetime')
        if summary.count() > 0:
            recent_summary = summary[0]
        else:
            recent_summary = None
    
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST' 

    return render_to_response('dictionary/view.html', {
        'result' : result,
        'course' : course,
        'professors' : course.professors,
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

        comments = Comment.objects.filter(course=course, lecture=lecture)
        score_average = comments.annotate(Avg('score'))
        load_average = comments.annotate(Avg('load'))
        gain_average = comments.anotate(Avg('gain'))
        Course.objects.filter(id=course.id).update(score_average=score_average, load_average=load_average, gain_average=gain_average)

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

# -- Private functions
def _search(**conditions):
    department = conditions.get('dept', None)
    type = conditions.get('type', None)
    lang = conditions.get('lang', 'ko')
    keyword = conditions.get('keyword', None)

    output = Course.objects.all()

    if department != None and type != None and keyword != None:
        keyword = keyword.strip()
        if department == u'-1' and type == u'전체보기':
            raise ValidationError()
        if department != u'-1':
            output = output.objects.filter(type__exact=type)
        if type != u'전체보기':
            output = output.objects.filter(department__id__exact=int(department))
        if keyword != u'':
            words = keyword.split()
            for word in words:
                output = output.filter(Q(old_code__icontains=word) | Q(title__icontains=word) | Q(professors__professor_name__icontains=word)).distinct()
    else:
        raise ValidationError()

    return output

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

def _courses_to_output(courses):
    all = []
    if not isinstance(courses, list):
        courses = courses.select_related()
    for course in courses:
        item = {
                'id': course.id,
                'course_no': course.old_code,
                'dept_id': course.department.id,
                'type': course.type,
                'title': course.title
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
