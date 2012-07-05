# -*- coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator
from django.core.exceptions import *
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.http import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Max
from django.utils.html import strip_tags, escape
from django.utils import simplejson as json
from otl.apps.favorites.models import CourseLink
from otl.apps.common import *
from otl.utils import respond_as_attachment
from otl.utils.decorators import login_required_ajax
from otl.apps.accounts.models import Department, UserProfile
from otl.apps.timetable.models import Lecture
from otl.apps.dictionary.models import *
from otl.apps.timetable.views import _lectures_to_output

from django import template
template.add_to_builtins('django.templatetags.i18n')

from django.utils.translation import ugettext
from StringIO import StringIO
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

    todo_comment_list = []
    if request.user.is_authenticated():
        comment_lecture_list = _get_unwritten_lecture_by_db(request.user)
        todo_comment_list = _lectures_to_output(comment_lecture_list, False, request.session.get('django_language','ko'))
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
        'rank_list' : _top_by_score(10),
        'taken_credits' : u'넘겨줘',
        'taken_au' : u'넘겨줘',
        'planned_credits' : u'넘겨줘',
        'planned_au' : u'넘겨줘',
        'recent_rank_list' : _top_by_recent_score(10),
        'todo_comment_list' : todo_comment_list,
        'dept': -1,
        'classification': 0,
        'keyword': json.dumps('',ensure_ascii=False,indent=4), 
        'in_category': json.dumps(False),
        'active_tab': -1,
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

        output = _courses_to_output(_search(**q),False,request.session.get('django_language','ko'))
        return HttpResponse(json.dumps(output, ensure_ascii=False, indent=4))
    except:
        return HttpResponseBadRequest()

def get_autocomplete_list(request):
    try:
        def reduce(list):
            return [item for sublist in list for subsublist in sublist for item in subsublist]
        q = {}

        department = request.GET.get('dept', None)
        type = request.GET.get('type', None)
        lang = request.GET.get('lang', 'ko')

        output = None
        cache_key = 'autocomplete-list-dict-cache:department=%s:type=%s:lang=%s'%(department,type,lang)
        output = cache.get(cache_key)
        if output is None:
            if lang == 'ko':
                func = lambda x:[[x.title, x.old_code],map(lambda y : y.professor_name,x.professors.all())] 
            elif lang == 'en':
                func = lambda x:[[x.title_en,x.old_code], map(lambda y: y.professor_name_en,x.professors.all())] 
            result = list(set(reduce(map(func, _search_by_dt(department, type)))))
            while None in result:
                result[result.index(None)] = 'None'
            output = json.dumps(result, ensure_ascii=False, indent=4)
            cache.set(cache_key, output, 3600)
        return HttpResponse(output)
    except:
        return HttpResponseBadRequest()

def show_more_comments(request):
    course_id = int(request.GET.get('course_id', -1))
    next_comment_id = int(request.GET.get('next_comment_id', -1))
    course = Course.objects.get(id=course_id) 
    if next_comment_id == -1:  #starting point
        comments = Comment.objects.all().order_by('-id')[:settings.COMMENT_NUM]
    elif next_comment_id == -2 : #nothing 
        return HttpResponse(json.dumps({
            'next_comment_id':0,
            'comments':[]}))
    else:
        comments = Comment.objects.filter(course=course,id__lte=next_comment_id).order_by('-id')[:settings.COMMENT_NUM]
    lang=request.session.get('django_language','ko')
    comments_output = _comments_to_output(comments,False,lang)
  
    if len(comments) == 0 :
        return HttpResponse(json.dumps({
            'next_comment_id': -2,
            'comments':comments_output}))
    return HttpResponse(json.dumps({
        'next_comment_id': (comments[len(comments)-1].id)-1,
        'comments': comments_output}))


def view(request, course_code):
    course = None
    recent_summary = None

    try:
        dept = int(request.GET.get('dept', -1))
        classification = int(request.GET.get('classification', 0))
        keyword = request.GET.get('keyword', "")
        in_category = request.GET.get('in_category', json.dumps(False))
        active_tab = int(request.GET.get('active_tab', -1))

        course = Course.objects.get(old_code=course_code.upper())
        summary = Summary.objects.filter(course=course).order_by('-id')
        lang=request.session.get('django_language','ko')
        if summary.count() > 0:
            recent_summary = summary[0]
        else:
            recent_summary = None
    
        course_output = _courses_to_output(course,True,lang)
        lectures_output = _lectures_to_output(Lecture.objects.filter(course=course), True, lang)
        professors_output = _professors_to_output(course.professors,True,lang) 
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST' 

    return render_to_response('dictionary/view.html', {
        'result' : result,
        'lang' : request.session.get('django_language', 'ko'),
        'departments': Department.objects.filter(visible=True).order_by('name'),
        'course' : course_output,
        'lectures' : lectures_output,
        'professors' : professors_output,
        'summary' : recent_summary,
        'dept': dept,
        'classification': classification,
        'keyword': keyword,
        'in_category': in_category,
        'active_tab': active_tab
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
        'comments': _comments_to_output(comments,False,request.session.get('django_language','ko'))}, ensure_ascii=False, indent=4))

@login_required_ajax
def add_comment(request):
    try:
        lecture_id = int(request.POST.get('lecture_id', -1)) 
        new_comment= Comment.objects.none()
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
        
        lectures = _get_taken_lecture_by_db(request.user, course)
        if lectures == Lecture.objects.none():
            lecture = None
        else:
            lecture = lectures[0]   # 여러번 들었을 경우 가장 최근에 들은 과목 기준으로 한다.

        comment = request.POST.get('comment', None)
        load = int(request.POST.get('load', -1))
        gain = int(request.POST.get('gain', -1))
        score = int(request.POST.get('score', -1))
        writer = request.user

        if load < 0 or gain < 0 or score < 0:
            raise ValidationError()

        #if Comment.objects.filter(course=course, lecture=lecture, writer=writer).count() > 0:
        #    raise AlreadyWrittenError()

        new_comment = Comment(course=course, lecture=lecture, writer=writer, comment=comment, load=load, score=score, gain=gain)
        new_comment.save()

        comments = Comment.objects.filter(course=course)      
        new_comment = Comment.objects.filter(id=new_comment.id)      
        average = comments.aggregate(avg_score=Avg('score'),avg_gain=Avg('gain'),avg_load=Avg('load'))
        Course.objects.filter(id=course.id).update(score_average=average['avg_score'], load_average=average['avg_load'], gain_average=average['avg_gain'])

        result = 'ADD'

        # update writer score
        user_profile = UserProfile.objects.get(user=writer)
        user_profile.score = user_profile.score + COMMENT_SCORE
        user_profile.recent_score = user_profile.recent_score + COMMENT_SCORE
        user_profile.save()

    except AlreadyWrittenError:
        result = 'ALREADY_WRITTEN'
        return HttpResponse(json.dumps({
            'result':result},  ensure_ascii=False, indent=4))
    except ValidationError:
        return HttpResponseBadRequest()
    #except:
    #    return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'average': average,
        'comment': _comments_to_output(new_comment, False, request.session.get('django_language','ko'))}, ensure_ascii=False, indent=4))
            
@login_required_ajax
def delete_comment(request):
    average = {'score':0, 'gain':0, 'load':0}
    try:
        user = request.user
        comment_id = int(request.POST.get('comment_id', -1))

        if comment_id < 0:
            raise ValidationError()
        comment = Comment.objects.get(pk=comment_id, writer=user)
        comment.delete()

        result = 'DELETE'

        course = comment.course
        lecture = comment.lecture
        comments = Comment.objects.filter(course=course)
        if comments.count() != 0 :
            average = comments.aggregate(avg_score=Avg('score'),avg_gain=Avg('gain'),avg_load=Avg('load'))
            Course.objects.filter(id=course.id).update(score_average=average['avg_score'],load_average=average['avg_load'],gain_average=average['avg_gain'])
        else :
            Course.objects.filter(id=course.id).update(score_average=0,load_average=0,gain_average=0)

        # update writer score
        user_profile = UserProfile.objects.get(user=user)
        user_profile.score = user_profile.score - COMMENT_SCORE
        user_profile.recent_score = user_profile.recent_score - COMMENT_SCORE
        user_profile.save()

    except ObjectDoesNotExist:
        result = 'REMOVE_NOT_EXIST'
    except ValidationError:
        return HttpResponseBadReqeust()
    #except:
    #    return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result, 'average': average}, ensure_ascii=False, indent=4)) 


def update_comment(request):
    comments = []

    try:
        count = int(request.POST.get('count', -1))
        q = {}
        if request.user.is_authenticated():
            user = request.user
            userprofile = UserProfile.objects.get(user=user)
            q['dept'] = userprofile.department
            comments = _update_comment(count, **q)
        else:
            comments = _update_comment(count, **q)
        result = 'OK'

    except ObjectDoesNotExist:
        result = 'ERROR'

    return HttpResponse(json.dumps({
        'result': result,
        'comments': _comments_to_output(comments,False,request.session.get('django_language','ko')) }, ensure_ascii=False, indent=4))


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
        written_datetime = datetime.datetime.now()
        new_summary = Summary(summary=content, writer=writer, written_datetime=written_datetime, course=course)
        new_summary.save()
        result = 'OK'
    except ValidationError:
        return HttpResponseBadReqeust()
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'summary': _summary_to_output([new_summary],False,'ko')}, ensure_ascii=False, indent=4))


# -- Private functions
def _trans(ko_message, en_message, lang) :
    if en_message == None or lang == 'ko' :
        return ko_message
    else :
        return en_message

def _top_by_score(count):
    rank_list = UserProfile.objects.all().order_by('-score')
    rank_list_size = rank_list.count()
    rank_list_with_index = []
    for i in xrange(count):
        if rank_list_size > i :
            item = {
                    'index':i+1,
                    'user' :rank_list[i]
                    }
            rank_list_with_index.append(item)
    return rank_list_with_index

def _top_by_recent_score(count):
    rank_list = UserProfile.objects.all().order_by('-recent_score')
    rank_list_size = rank_list.count()
    rank_list_with_index = []
    for i in xrange(count):
        if rank_list_size > i :
            item = {
                    'index':i+1,
                    'user' :rank_list[i]
                    }
            rank_list_with_index.append(item)
    return rank_list_with_index

def _update_comment(count, **conditions):
    department = conditions.get('dept', None)
    if department != None:
        comments = Comment.objects.filter(course__department=department)
    else:
        comments = Comment.objects.all().order_by('-id')
    comments_size = comments.count()
    if comments_size < count:
        return comments[0:comments_size]
    return comments[0:count]

def _search(**conditions):
    department = conditions.get('dept', None)
    type = conditions.get('type', None)
    lang = conditions.get('lang', 'ko')
    keyword = conditions.get('keyword', None)

    if department != None and type != None and keyword != None:
        keyword = keyword.strip()
        output = _search_by_dt(department, type) 
        if keyword == u'':
            if department == u'-1' and type == u'전체보기':
                raise ValidationError()
        else:
            words = keyword.split()
            for word in words:
                if lang=='ko':
                    output = output.filter(Q(old_code__icontains=word) | Q(title__icontains=word) | Q(professors__professor_name__icontains=word)).distinct()
                elif lang=='en':
                    output = output.filter(Q(old_code__icontains=word) | Q(title_en__icontains=word) | Q(professors__professor_name_en__icontains=word)).distinct()
    else:
        raise ValidationError()

    return output

def _search_by_dt(department, type):
    cache_key = 'dictionary-search-cache:department=%s:type=%s' % (department,type)
    output = cache.get(cache_key)
    if output is None:
        output = Course.objects.all()
        if department != u'-1':
            output = output.filter(department__id__exact=int(department))
        if type != u'전체보기':
            output = output.filter(type__exact=type)
        cache.set(cache_key,output,3600)
    return output

def _comments_to_output(comments,conv_to_json=True, lang='ko'):
    all = []
    if not isinstance(comments, list):
        comments = comments.select_related()
    for comment in comments:
        writer = comment.writer
        try:
            profile = UserProfile.objects.get(user=writer)
            nickname = profile.nickname
        except:
            nickname = ''
        if comment.lecture == None:
            lecture_id = -1
        else:
            lecture_id = comment.lecture.id
        item = {
            'comment_id': comment.id,
            'course_id': comment.course.id,
            'course_title': _trans(comment.course.title,comment.course.title_en,lang),
            'lecture_id': lecture_id,
            'writer_id': comment.writer.id,
            'writer_nickname': nickname,
            'professor': _professors_to_output(_get_professor_by_lecture(comment.lecture),False,lang),
            'written_datetime': comment.written_datetime.isoformat(),
            'comment': comment.comment,
            'score': comment.score,
            'gain': comment.gain,
            'load': comment.load,
            'like': comment.like
        }
        all.append(item)
    if conv_to_json:
        io = StringIO()
        if settings.DEBUG:
            json.dump(all,io,ensure_ascii=False,indent=4)
        else:
            json.dump(all,io,ensure_ascii=False,sort_keys=False,separators=(',',':'))
        return io.getvalue()
    else :
        return all

def _professors_to_output(professors,conv_to_json=True,lang='ko'):
    all = []
    if not isinstance(professors, list):
        professors = professors.select_related()
    for professor in professors:
        item = {
                'professor_name': _trans(professor.professor_name,professor.professor_name_en,lang),
                'professor_id': professor.professor_id
                }
        all.append(item)
    if conv_to_json:
        io = StringIO()
        if settings.DEBUG:
            json.dump(all,io,ensure_ascii=False,indent=4)
        else:
            json.dump(all,io,ensure_ascii=False,sort_keys=False,separators=(',',':'))
        return io.getvalue()
    else :
        return all

def _courses_to_output(courses,conv_to_json=True,lang='ko'):
    all = []
    if isinstance(courses, Course):
        item = {
                'id': courses.id,
                'old_code': courses.old_code,
                'dept_id': courses.department.id,
                'type': _trans(courses.type,courses.type_en,lang),
                'title': _trans(courses.title,courses.title_en,lang),
                'score_average': courses.score_average,
                'load_average': courses.load_average,
                'gain_average': courses.gain_average
                }
        if conv_to_json:
            io = StringIO()
            if settings.DEBUG:
                json.dump(item,io,ensure_ascii=False,indent=4)
            else:
                json.dump(item,io,ensure_ascii=False,sort_keys=False,separators=(',',':'))
            return io.getvalue()
        else :
            return item

    if not isinstance(courses, list):
        courses = courses.select_related()
    for course in courses:
        item = {
                'id': course.id,
                'old_code': course.old_code,
                'dept_id': course.department.id,
                'type': _trans(course.type,course.type_en,lang),
                'title': _trans(course.title,course.title_en,lang),
                'score_average': course.score_average,
                'load_average': course.load_average,
                'gain_average': course.gain_average
                }
        all.append(item)
    if conv_to_json:
        io = StringIO()
        if settings.DEBUG:
            json.dump(all,io,ensure_ascii=False,indent=4)
        else:
            json.dump(all,io,ensure_ascii=False,sort_keys=False,separators=(',',':'))
        return io.getvalue()
    else :
        return all

def _summary_to_output(summaries,conv_to_json=True,lang='ko'):
    all = []
    if not isinstance(summaries, list):
        summaries = summaries.select_related()
    for summary in summaries:
        item = {
            'summary': summary.summary,
            'writer_id': summary.writer.id,
            'written_datetime': summary.written_datetime,
            'course_id': summary.course.id
            }
        all.append(item) 
    if conv_to_json:
        io = StringIO()
        if settings.DEBUG:
            json.dump(item,io,ensure_ascii=False,indent=4)
        else:
            json.dump(item,io,ensure_ascii=False,sort_keys=False,separators=(',',':'))
        return io.getvalue()
    else :
        return all

def _get_professor_by_lecture(lecture):
    if lecture == None:
        return Professor.objects.none()
    return lecture.professor.all()

def _get_taken_lecture_by_db(user, course):
    try:
        lectures = Lecture.objects.filter(course=course)
        take_lecture_list = UserProfile.objects.get(user=user).take_lecture_list

        result = take_lecture_list.filter(course=course).order_by('-year','-semester')

        return result
    except ObjectDoesNotExist:
        return Lecture.objects.none()

def _get_unwritten_lecture_by_db(user):
    try:
        take_lecture_list = UserProfile.objects.get(user=user).take_lecture_list.all()
    except ObjectDoesNotExist:
        return Lecture.objects.none()

    try:
        comment_list = Comment.objects.filter(writer=user)
    except ObjectDoesNotExist :
        comment_list = []
   
    ret_list = list(take_lecture_list)
    for comment in comment_list:
        if comment.lecture in ret_list:
            ret_list.remove(comment.lecture)
    return ret_list
