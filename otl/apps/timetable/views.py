# -*- coding: utf-8-*-

import os, tempfile, httplib
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.db.models import Count
from django.db import IntegrityError
from django.http import *
from django.template import RequestContext
from django.utils import simplejson as json
from django.conf import settings
from django.core.exceptions import *
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from otl.utils import respond_as_attachment, get_choice_display
from otl.utils.decorators import login_required_ajax
from otl.apps.common import *
from otl.apps.accounts.models import Department, UserProfile
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus, Timetable, OverlappingTimeError, OverlappingExamTimeError
from StringIO import StringIO
from django.db.models import Q
from otl.apps.dictionary.models import Professor
from django.core.servers.basehttp import FileWrapper
from datetime import timedelta, datetime
import Image

from django import template
template.add_to_builtins('django.templatetags.i18n')

from django.utils.translation import ugettext,activate
import hashlib
import MySQLdb

import gflags
import httplib2
import json

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

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
        my_lectures = [_lectures_to_output(Lecture.objects.filter(year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER, id__in=request.session.get('lectures_%s_%s_%s' % (id, unicode(settings.NEXT_YEAR), unicode(settings.NEXT_SEMESTER)), [])), False, request.session.get('django_language', 'ko')) for id in xrange(0,settings.NUMBER_OF_TABS)]

    if settings.DEBUG:
        my_lectures_output = json.dumps(my_lectures, indent=4, ensure_ascii=False)
    else:
        my_lectures_output = json.dumps(my_lectures, ensure_ascii=False, sort_keys=False, separators=(',',':'))
    
    # Delete the timetable item if the corresponding lecture is marked as deleted.
    # However, we already added this item to my_lectures to notify the user at least once.
    if request.user.is_authenticated():
        Timetable.objects.filter(user=request.user, lecture__year__exact=settings.NEXT_YEAR, lecture__semester=settings.NEXT_SEMESTER, lecture__deleted=True).delete()

    return render_to_response('timetable/index.html', {
        'section': 'timetable',
        'title': ugettext(u'모의시간표'),
        'departments': Department.objects.filter(visible=True).order_by('name'),
        'my_lectures': my_lectures_output,
        'lang' : request.session.get('django_language', 'ko'),
        'semester_info' : semester_info,
    }, context_instance=RequestContext(request))

def search(request):
    try:
        # Convert QueryDict to a normal python dict.
        q = {}
        for key, value in request.GET.iteritems():
            q[str(key)] = value

        if (set(q.keys()) == set(('dept', 'type', 'lang', 'keyword', 'year', 'term'))
                and q['keyword'] == u''):
            cache_key = ('search:year=%s:semester=%s:department=%s:type=%s:lang=%s:' %
                         (q['year'], q['term'], q['dept'], q['type'], q['lang']))
            output = cache.get(cache_key)
            if output is None:
                output = _lectures_to_output(_search(**q), True, request.session.get('django_language', 'ko'))
                cache.set(cache_key, output, 3600)
        else:
            output = _lectures_to_output(_search(**q), True, request.session.get('django_language', 'ko'))

        return HttpResponse(output)

    except ValidationError:
        return HttpResponseBadRequest()

def get_autocomplete_list(request):
    try:
        def reduce(list):
            return [item for sublist in list for subsublist in sublist for item in subsublist]
        year = request.GET.get('year', unicode(settings.NEXT_YEAR))
        semester = request.GET.get('term', unicode(settings.NEXT_SEMESTER))
        department = request.GET.get('dept', None)
        type = request.GET.get('type', None)
        lang = request.GET.get('lang', 'ko')

        cache_key = 'autocomplete-list-cache:year=%s:semester=%s:department=%s:type=%s:lang=%s' % (year, semester, department, type, lang)
        output = cache.get(cache_key)
        if output is None:
            if lang == 'ko':
                func = lambda x:[[x.title,x.old_code], map(lambda y:y.professor_name,x.professor.all())] 
            elif lang == 'en':
                func = lambda x:[[x.title_en,x.old_code],map(lambda y:y.professor_name_en,x.professor.all())] 
            result = list(set(reduce(map(func, _search_by_ysdt(year, semester, department, type)))))
            while None in result:
                result[result.index(None)] = 'None'
            output = json.dumps(result, ensure_ascii=False, indent=4)
            cache.set(cache_key, output, 3600)
        return HttpResponse(output)
    except:
        return HttpResponseBadRequest()

def get_comp_rate(request):
    year = request.GET.get('year', unicode(settings.NEXT_YEAR))
    semester = request.GET.get('term', unicode(settings.NEXT_SEMESTER))
    old_code = request.GET.get('course_no', None)
    class_no = request.GET.get('class_no', None)

    try:
        lecture = Lecture.objects.get(year=int(year), semester=int(semester), old_code=old_code, class_no=class_no)
        result = {'limit': lecture.limit, 'num_people': lecture.num_people}
        io = StringIO()
        if settings.DEBUG:
            json.dump(result, io, ensure_ascii=False, indent=4)
        else:
            json.dump(result, io, ensure_ascii=False, sort_keys=False, separators=(',',':'))
        return HttpResponse(io.getvalue())
    except:
        raise ValidationError('lecture is not exist')

@login_required_ajax
def add_to_timetable(request):
    user = request.user
    table_id = request.GET.get('table_id', None)
    lecture_id = request.GET.get('lecture_id', None)
    view_year = request.GET.get('view_year', unicode(settings.NEXT_YEAR))
    view_semester = request.GET.get('view_semester', unicode(settings.NEXT_SEMESTER))
    
    lectures = []
    try:
        lecture = Lecture.objects.get(pk=lecture_id)

        if user.is_authenticated():
            lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=view_year, semester=view_semester)
        else:
            session_key = 'lectures_%s_%s_%s' % (table_id, view_year, view_semester)
            lecture_ids = request.session.get(session_key, [])
            lectures = Lecture.objects.filter(year=view_year, semester=view_semester,id__in=lecture_ids) 


        for existing_lecture in lectures:
            if existing_lecture.check_classtime_overlapped(lecture):
                raise OverlappingTimeError()
            if existing_lecture.check_examtime_overlapped(lecture):
                raise OverlappingExamTimeError()

        if user.is_authenticated():
            timetable = Timetable(user=user, lecture=lecture, year=lecture.year, semester=lecture.semester, table_id=table_id)
            timetable.save()

            lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=view_year, semester=view_semester)
        else:
            session_key = 'lectures_%s_%s_%s' % (table_id, view_year, view_semester)
            lecture_ids = request.session.get(session_key, [])
            lectures = Lecture.objects.filter(year=view_year, semester=view_semester,id__in=lecture_ids) 

        result = 'OK'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST'
    except OverlappingTimeError:
        result = 'OVERLAPPED'
    except IntegrityError:
        result = 'DUPLICATED'
    except OverlappingExamTimeError:
        result = 'OVERLAPPEDEXAMTIME'
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'data': _lectures_to_output(lectures, False, request.session.get('django_language', 'ko')),
    }, ensure_ascii=False, indent=4))

@login_required_ajax
def delete_from_timetable(request):
    user = request.user
    table_id = request.GET.get('table_id', None)
    lecture_id = request.GET.get('lecture_id', None)
    view_year = request.GET.get('view_year', unicode(settings.NEXT_YEAR))
    view_semester = request.GET.get('view_semester', unicode(settings.NEXT_SEMESTER))

    lectures = []
    try:
        if user.is_authenticated():
            if lecture_id is None:
                Timetable.objects.filter(user=user, year=view_year, semester=view_semester, table_id=table_id).delete()
            else:
                lecture = Lecture.objects.get(pk=lecture_id)
                Timetable.objects.get(user=user, lecture=lecture, year=lecture.year, semester=lecture.semester, table_id=table_id).delete()

            lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=view_year, semester=view_semester)
        else:
            session_key = 'lectures_%s_%s_%s' % (table_id, view_year, view_semester)
            if lecture_id is None:
                del request.session[session_key]
            else:
                lecture_list = request.session.get(session_key, [])
                lecture_list.remove(int(lecture_id))
                request.session[session_key] = lecture_list
            lectures = Lecture.objects.filter(year=view_year, semester=view_semester,id__in=lecture_list) 
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST'
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'data': _lectures_to_output(lectures, False, request.session.get('django_language', 'ko')),
    }, ensure_ascii=False, indent=4))

@login_required_ajax
def view_timetable(request):
    user = request.user
    table_id = request.GET.get('table_id', None)
    view_year = request.GET.get('view_year', None)
    view_semester = request.GET.get('view_semester', None)

    lectures = []
    try:
        lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'OK'
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'data': _lectures_to_output(lectures, False, request.session.get('django_language', 'ko')),
    }, ensure_ascii=False, indent=4))

@login_required_ajax
def change_semester(request):
    user = request.user
    view_year = request.GET.get('view_year', unicode(settings.NEXT_YEAR))
    view_semester = request.GET.get('view_semester', unicode(settings.NEXT_SEMESTER))

    try:
        if user.is_authenticated():
            my_lectures = [_lectures_to_output(Lecture.objects.filter(year=view_year, semester=view_semester, timetable__user=user, timetable__table_id=id), False, request.session.get('django_language', 'ko')) for id in xrange(0,settings.NUMBER_OF_TABS)]
        else:
            my_lectures = [_lectures_to_output(Lecture.objects.filter(year=view_year, semester=view_semester, id__in=request.session.get('lectures_%s_%s_%s' % (id, view_year, view_semester), [])), False, request.session.get('django_language', 'ko')) for id in xrange(0,settings.NUMBER_OF_TABS)]
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'OK'
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'data': my_lectures,
    }, ensure_ascii=False, indent=4))

def calendar(request):
    user = request.user
    try:
        userprofile = UserProfile.objects.get(user=user)
    except:
        raise ValidationError('no user profile')

    email = userprofile.email
    if email is None:
        return HttpResponse(json.dumps({
            'result': 'EMPTY',
            }, ensure_ascii=False, indent=4))
    table_id = int(request.GET.get('id', 0))
    view_year = int(request.GET.get('view_year', settings.NEXT_YEAR))
    view_semester = int(request.GET.get('view_semester', settings.NEXT_SEMESTER))
    start = settings.SEMESTER_RANGES[(view_year,view_semester)][0]
    end = settings.SEMESTER_RANGES[(view_year,view_semester)][1] + timedelta(days=1)
    lang = request.session.get('django_language', 'ko')

    FLAGS = gflags.FLAGS
    FLAGS.auth_local_webserver = False

    json_data = open('/home/chaos/calendar/client_secrets.json')
    data = json.load(json_data)
    client_id = data['installed']['client_id']
    client_secret = data['installed']['client_secret']
    api_key = data['api_key']
    FLOW = OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope='https://www.googleapis.com/auth/calendar',
        user_agent='')

    storage = Storage('/home/chaos/calendar/calendar.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
      credentials = run(FLOW, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build(serviceName='calendar', version='v3', http=http,
           developerKey=api_key)

    calendar_name = "[OTL]" + userprofile.nickname + "'s calendar"
    calendar = None
    if userprofile.calendar_id != None:
        try:
            calendar = service.calendars().get(calendarId = userprofile.calendar_id).execute()
            if calendar != None and calendar['summary'] != calendar_name:
                calendar['summary'] = calendar_name
                calendar = service.calendars().update(calendarId = calendar['id'], body = calendar).execute()
        except:
            pass

    if calendar == None:
        calendar_entry = {
                'summary' : calendar_name,
                'timeZone' : 'Asia/Seoul'
                }
        calendar = service.calendars().insert(body = calendar_entry).execute()

        calendar_list = service.calendarList().get(calendarId = calendar['id']).execute()
        calendar_list['hidden'] = True
        reminder = {
                'method' : 'popup',
                'minutes' : 10
                }
        calendar_list['defaultReminders']=[reminder]
        calendar_list = service.calendarList().update(calendarId = calendar['id'], body = calendar_list).execute()

        userprofile.calendar_id = calendar['id']
        userprofile.save()

    acl_list = service.acl().list(calendarId = calendar['id']).execute()
    is_email_exist = False
    for old_rule in acl_list['items']:
        if old_rule['scope']['value'] == userprofile.email:
            is_email_exist = True
            break

    if not is_email_exist:
        rule = {
                'scope' : {
                    'type' : 'user',
                    'value' : userprofile.email
                    },
                'role' : 'owner'
                }
        service.acl().insert(calendarId = calendar['id'], body = rule).execute()

    #TODO google calendar invitation email
    events = service.events().list(calendarId = calendar['id'], maxResults=2000,
            timeMin = str(start) + "T00:00:00+09:00",
            timeMax = str(end) + "T00:00:00+09:00").execute()
    for event in events['items']:
        service.events().delete(calendarId = calendar['id'], eventId = event['id']).execute()

    my_lectures = Lecture.objects.filter(year=view_year, semester=view_semester, timetable__user=user, timetable__table_id=table_id).select_related()
    for lecture in my_lectures:
        classtimes = ClassTime.objects.filter(lecture=lecture)
        for classtime in classtimes:
            days_ahead = classtime.day - start.weekday()
            if days_ahead < 0:
                days_ahead += 7
            class_date = start + timedelta(days = days_ahead)

            event = {
                    'summary' : lecture.title,
                    'location' : _trans(classtime.room_ko, classtime.room_en, lang) + " " + classtime.room,
                    'start' : {
                        'dateTime' : datetime.combine(class_date, classtime.begin).isoformat(),
                        'timeZone' : 'Asia/Seoul'
                        },
                    'end' : {
                        'dateTime' : datetime.combine(class_date, classtime.end).isoformat(),
                        'timeZone' : 'Asia/Seoul'
                        },
                    'recurrence' : ['RRULE:FREQ=WEEKLY;UNTIL=' + end.strftime("%Y%m%d")],
                    }

            service.events().insert(calendarId = calendar['id'], body = event).execute()

    return HttpResponse(json.dumps({
        'result': 'OK',
         }, ensure_ascii=False, indent=4))

# -- Private functions --

def _trans(ko_message, en_message, lang):
    if en_message == None or lang == 'ko':
        return ko_message
    else:
        return en_message

def _search(**conditions):
    year = conditions.get('year', unicode(settings.NEXT_YEAR))
    semester = conditions.get('term', unicode(settings.NEXT_SEMESTER))
    department = conditions.get('dept', None)
    type = conditions.get('type', None)
    lang = conditions.get('lang', 'ko')
    keyword = conditions.get('keyword', None)
    day_begin = conditions.get('start_day', None)
    day_end = conditions.get('end_day', None)
    time_begin = conditions.get('start_time', None)
    time_end = conditions.get('end_time', None)

    # This query requires Django 1.1 or newer.
    lectures = _search_by_ys(year, semester)

    #try:
    if year == None or semester == None:
        raise ValidationError('year or semester is null')
    if day_begin != None and day_end != None and time_begin != None and time_end != None:
        if int(time_end) == 24*60:
            # 24:00가 종료시간인 경우 처리
            day_end = int(day_end)
            if day_end < 6:
                day_end += 1
            time_end = 0
        if day_begin == day_end:
            lectures = lectures.filter(classtime__day__exact=int(day_begin),
                                       classtime__begin__gte=ClassTime.numeric_time_to_obj(int(time_begin)),
                                       classtime__end__lte=ClassTime.numeric_time_to_obj(int(time_end)))
        else:
            lectures = lectures.filter(classtime__day__gte=int(day_begin), classtime__day__lte=int(day_end),
                                       classtime__begin__gte=ClassTime.numeric_time_to_obj(int(time_begin)),
                                       classtime__end__lte=ClassTime.numeric_time_to_obj(int(time_end)))
        lectures = lectures.order_by('type', 'code').distinct().select_related()
    elif department != None and type != None and keyword != None:
        keyword = keyword.strip()
        if keyword == u'':
            if department == u'-1' and type == u'전체보기':
                raise ValidationError('department and type is all')
            lectures = _search_by_ysdt(year, semester, department, type)
        else:
            words = [keyword] #keyword.split()
            lectures = None
            for word in words:
                result = _search_by_ysdtlw(year, semester, department, type, lang, unicode(word))
                if lectures is None:
                    lectures = result
                else:
                    lectures = lectures & result
            lectures = lectures.order_by('type', 'code').distinct().select_related()
    else:
        raise ValidationError('some key is null')
    #except (TypeError, ValueError):
    #    raise ValidationError()

    return lectures

def _search_by_ys(year, semester):
    cache_key = 'timetable-search-cache:year=%s:semester=%s' % (year, semester)
    output = cache.get(cache_key)
    if output is None:
        output = Lecture.objects.annotate(num_classtimes=Count('classtime')).filter(year=int(year), semester=int(semester), num_classtimes__gt=0, deleted=False)
        cache.set(cache_key, output, 3600)
    return output

def _search_by_ysdt(year, semester, department, type):
    cache_key = 'timetable-search-cache:year=%s:semester=%s:department=%s:type=%s' % (year, semester, department, type)
    output = cache.get(cache_key)
    if output is None:
        output = _search_by_ys(year, semester)
        if department != u'-1':
            output = output.filter(department__id__exact=int(department))
        if type != u'전체보기':
            output = output.filter(type__exact=type)
        output = output.order_by('type', 'code').distinct().select_related()
        cache.set(cache_key, output, 3600)
    return output

def _search_by_ysdtlw(year, semester, department, type, lang, word):
    word_hash = hashlib.md5(word.encode("utf-8")).hexdigest()
    cache_key = 'timetable-search-cache:year=%s:semester=%s:department=%s:type=%s:lang=%s:word=%s' % (year, semester, department, type, lang, word_hash)
    output = cache.get(cache_key)
    if output is None:
        output = _search_by_ysdt(year, semester, department, type)
        if lang == 'ko':
            professor_ids = Professor.objects.filter(professor_name__icontains=word).values_list('id',flat=True)
            output = output.filter(Q(old_code__icontains=word) | Q(title__icontains=word) | Q(professor__id__in=professor_ids)).distinct() 
        else:
            professor_ids = Professor.objects.filter(professor_name_en__icontains=word).values_list('id',flat=True)
            output = output.filter(Q(old_code__icontains=word) | Q(title_en__icontains=word) | Q(professor__id__in=professor_ids)).distinct() 
        cache.set(cache_key, output, 3600)
    return output

def _lectures_to_output(lectures, conv_to_json=True, lang='ko'):
    all = []
    if not isinstance(lectures, list):
        lectures = lectures.select_related()
    for lecture in lectures:
        try:
            exam = lecture.examtime_set.get() # 첫번째 항목만 가져옴
        except:
            exam = None
        if lang == 'ko':
            classtimes = [{'day': schedule.day, 'start': schedule.get_begin_numeric(), 'end': schedule.get_end_numeric(), 'classroom': schedule.get_location(), 'type': schedule.get_type_display(), '_type': schedule.type} for schedule in lecture.classtime_set.all()]
	else:
            classtimes = [{'day': schedule.day, 'start': schedule.get_begin_numeric(), 'end': schedule.get_end_numeric(), 'classroom': schedule.get_location_en(), 'type': schedule.get_type_display(), '_type': schedule.type} for schedule in lecture.classtime_set.all()]
        room = ''
        if len([item for item in classtimes if item['_type'] == 'l']) > 0:
            room = classtimes[0]['classroom']
        professors = lecture.professor.all()
        name=""
        for professor in professors:
            name += _trans(professor.professor_name, professor.professor_name_en, lang) +", "
        item = {
            'id': lecture.id,
            'dept_id': lecture.department.id,
            'classification': _trans(lecture.type, lecture.type_en, lang),
            'course_no': lecture.old_code,
            'class_no': lecture.class_no,
            'code': lecture.code,
            'title': _trans(lecture.title, lecture.title_en, lang),
            'lec_time': lecture.num_classes,
            'lab_time': lecture.num_labs,
            'credit': lecture.credit,
            'au': lecture.credit_au,
            'limit': lecture.limit,
            'num_people': lecture.num_people,
            'classroom': room,
            'deleted': lecture.deleted,
            'prof': name[:len(name)-2],
            'times': classtimes,
            'remarks': ugettext(u'영어강의') if lecture.is_english else u'',
            'examtime': {'day': exam.day, 'start': exam.get_begin_numeric(), 'end': exam.get_end_numeric()} if exam != None else None,
            'semester' : lecture.semester,
            'url' : "/dictionary/view/"+lecture.old_code+"/",
            'score_average': round(lecture.course.score_average,2),
            'load_average': round(lecture.course.load_average,2),
            'gain_average': round(lecture.course.gain_average,2)
        }
        all.append(item)
    if conv_to_json:
        io = StringIO()
        if settings.DEBUG:
            json.dump(all, io, ensure_ascii=False, indent=4)
        else:
            json.dump(all, io, ensure_ascii=False, sort_keys=False, separators=(',',':'))
        return io.getvalue()
    else:
        return all

def _get_color_by_index(index):
    modulecolors = ['#FFC7FE','#FFCECE','#DFE8F3','#D1E9FF','#D2F1EE','#FFEAD1','#E1D1FF','#FAFFC1','#D4FFC1','#DEDEDE','#BDBDBD']

    return modulecolors[ index % len(modulecolors) ]

def _render_html(request):
    table_id = int(request.GET.get('id', 0))
    view_year = int(request.GET.get('view_year', settings.NEXT_YEAR))
    view_semester = int(request.GET.get('view_semester', settings.NEXT_SEMESTER))

    my_lectures = _lectures_to_output(Lecture.objects.filter(year=view_year, semester=view_semester, timetable__user=request.user, timetable__table_id=table_id).select_related(), False, request.session.get('django_language', 'ko'))

    my_classes = []

    for i in xrange(len(my_lectures)):
        bgcolor = _get_color_by_index(i)

        lecture = my_lectures[i]

        if not lecture['deleted']:
            in_number = 0
            for time in lecture['times']:
                in_number += 1
                item = {
                    'bgcolor': bgcolor,
                    'course_no': lecture['course_no'],
                    'title': lecture['title'],
                    'classroom': lecture['classroom'],
                    'prof': lecture['prof'],
                    'left': time['day'] * 100 + 3,
                    'top': int((time['start'] - 480) / 30) * 21,
                    'height': int((time['end'] - time['start']) / 30) * 21 - 2,
                    'in_number': in_number,
                }

                my_classes.append(item)

    render_result = render_to_string('timetable/timetable.html', {
        'table_id': table_id,
        'my_classes': my_classes,
        'lang': request.session.get('django_language', 'ko'),
        'view_year': view_year,
        'view_semester': view_semester
    }, context_instance=RequestContext(request))

    return render_result

def _get_pdf(rendered_string):
    html_num, html_path = tempfile.mkstemp(suffix='.html', dir='/tmp')
    html_file = open(html_path, 'w')
    html_file.write(rendered_string.encode('utf-8'))
    html_file.close()

    pdf_num, pdf_path = tempfile.mkstemp(suffix='.pdf', dir='/tmp')

    cmd = 'prince -i=html --media=screen '

    css_list = ['default.css', 'layout.css', 'timetable.css', 'pdf_timetable.css', 'table.css']
    for css in css_list:
        cmd += '-s '
        cmd += os.path.join(settings.MEDIA_ROOT, css)
        cmd += ' '

    cmd += html_path
    cmd += ' -o ' + pdf_path

    os.system(cmd)

    return pdf_path


def _get_image(rendered_string):
    pdf_path = _get_pdf(rendered_string)

    img_tmp_num, img_tmp_path = tempfile.mkstemp(suffix='.png', dir='/tmp')
    img_num, img_path = tempfile.mkstemp(suffix='.png', dir='/tmp')

    os.system('gs -q -sDEVICE=png16m -dBATCH -dNOPAUSE -r400 -sOutputFile=%s %s' % (img_tmp_path, pdf_path))

    image = Image.open(img_tmp_path)
    result = image.resize((850, 1100), Image.ANTIALIAS).crop((120, 90, 730, 900))
    result.save(img_path, 'png')

    os.system('rm %s' % img_tmp_path)

    return img_path

@login_required
def print_as_pdf(request):
    table_id = request.GET.get('id', 0)
    view_year = request.GET.get('view_year', settings.NEXT_YEAR)
    view_semester = request.GET.get('view_semester', settings.NEXT_SEMESTER)
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    fd, temp_path = tempfile.mkstemp('otl-timetable.pdf')

    # Initialize (register fonts, creating canvas, calculating coords)
    sanserif_path = os.path.join(settings.MEDIA_ROOT, 'fonts/NanumGothic.ttf')
    sanserif_name = 'NanumGothic'
    sanserif_bold_path = os.path.join(settings.MEDIA_ROOT, 'fonts/NanumGothicBold.ttf')
    sanserif_bold_name = 'NanumGothicBold'
    serif_path = os.path.join(settings.MEDIA_ROOT, 'fonts/NanumMyeongjo.ttf')
    serif_name = 'NanumMyeongjo'
    pdfmetrics.registerFont(TTFont(sanserif_name, sanserif_path))
    pdfmetrics.registerFont(TTFont(sanserif_bold_name, sanserif_bold_path))
    pdfmetrics.registerFont(TTFont(serif_name, serif_path))
    # NOTE: all coordinates and sizes are measured in points.
    page_width = 841.89
    page_height = 595.27
    timelabels_width = 60.0 # width of the left time label area.
    header_height = 15.0    # height of the table header row.
    margin_x = 52.0         # distance from page border to left/right outmost grid lines.
    margin_y = 60.0         # distance from page border to top/bottom outmost grid lines.
    c = canvas.Canvas(temp_path, pagesize=(page_width, page_height))

    # Draw the outer layout.
    c.setFont(sanserif_bold_name, 18)
    c.drawCentredString(page_width / 2, page_height - margin_y + 12, u'%(year)d년 %(semester)s 시간표' % {
        'year': int(view_year),
        'semester': SEMESTER_TYPES[int(view_semester) - 1][1],
    })
    c.setFont(sanserif_name, 9)
    c.drawCentredString(page_width / 2, margin_y - 15, u'Generated by OTL, a proud service of SPARCS')
    c.setLineWidth(1.2)
    c.line(margin_x, page_height - margin_y, page_width - margin_x, page_height - margin_y)
    c.line(margin_x, margin_y, page_width - margin_x, margin_y)
    c.setLineWidth(1.0)
    c.line(margin_x, page_height - margin_y - header_height, page_width - margin_x, page_height - margin_y - header_height)

    # Draw the grid.
    column_width = (page_width - timelabels_width - margin_x * 2) / 5.0
    row_height = (page_height - (margin_y + header_height) - margin_y) / 32.0
    c.setLineWidth(0.12)
    for col in xrange(6):
        col_base = margin_x + timelabels_width + (column_width * col)
        c.line(col_base, margin_y, col_base, page_height - margin_y)
        c.drawCentredString(col_base + column_width / 2.0, page_height - (margin_y + 10), WEEKDAYS[col][1])
    c.setDash([2, 2], 0)
    for row in xrange(32):
        row_base = page_height - (margin_y + header_height) - (row_height * row)
        if row % 2 == 0:
            c.drawCentredString(margin_x + timelabels_width / 2.0, row_base - row_height + 4, u'%02d:00' % (8 + row / 2))
            c.line(margin_x, row_base, page_width - margin_x, row_base)

    def get_box_position(day, time_begin, time_end):
        left = margin_x + timelabels_width + (column_width * day)
        bottom = page_height - (margin_y + header_height) - (row_height * ((time_end - 480) / 30.0))
        return left, bottom, column_width, row_height * ((time_end - time_begin) / 30.0)

    def fit_text_width(text, max_width, font_name, font_size):
        # A code snippet from http://two.pairlist.net/pipermail/reportlab-users/2009-April/008198.html
        def locate_split(s, max_width, font_name='Times-Roman', font_size=12):
            def width(i, L=(len(s) + 1) * [None]):
                if L[i] is None:
                    L[i] = pdfmetrics.stringWidth(s[:i], font_name, font_size)
                return L[i]
            def brak(lo, hi):
                i = (lo + hi) >> 1
                if lo == i:
                    return lo
                if width(i) >= max_width:
                    return brak(lo, i)
                else:
                    return brak(i, hi)
            i = brak(0, len(s))
            if width(i) > max_width:
                i -= 1
            return i, width(i), width(i+1), s[:i+1]
        pos, lw, rw, text_after = locate_split(text, max_width, font_name, font_size)
        if text_after != text:
            pos, lw, rw, text_after = locate_split(text, max_width - pdfmetrics.stringWidth(u'...', font_name, font_size), font_name, font_size)
            return text_after + u'...'
        return text

    # Draw the actual timetable entries
    c.setDash([], 0)
    c.setLineWidth(0.5)
    my_lectures = Lecture.objects.filter(year=view_year, semester=view_semester, timetable__user=request.user, timetable__table_id=table_id).select_related()
    for lecture in my_lectures:
        classtimes = ClassTime.objects.filter(lecture=lecture)
        for classtime in classtimes:
            left, bottom, width, height = get_box_position(classtime.day, classtime.get_begin_numeric(), classtime.get_end_numeric())
            top = bottom + height
            offset = height / 2.0
            c.setFillColorRGB(0.92, 0.92, 0.92)
            c.roundRect(left, bottom, width, height, 4.0, 1, 1)
            c.setFillColorRGB(0, 0, 0)
            c.setFont(sanserif_bold_name, 9)
            title = lecture.title.replace(u'   ', u'')  # normalize
            c.drawCentredString(left + width / 2, bottom + offset + 4, fit_text_width(title, width - 5.0, sanserif_bold_name, 9))
            c.setFont(sanserif_name, 9)
            c.drawCentredString(left + width / 2, bottom + offset - row_height + 4, classtime.get_location())

    # Save and transfer.
    c.showPage()
    c.save()
    response = respond_as_attachment(request, temp_path, 'Timetable.pdf', True)
    os.remove(temp_path)
    return response

@login_required
def save_as_pdf(request):
    table_id = int(request.GET.get('id', 0))
    view_year = int(request.GET.get('view_year', settings.NEXT_YEAR))
    view_semester = int(request.GET.get('view_semester', settings.NEXT_SEMESTER))
    old_lang = request.session.get('django_language', 'ko')

    f = open(_get_pdf(_render_html(request)), 'rb')

    response = HttpResponse(FileWrapper(f), content_type='application/pdf')
    activate('en')
    response['Content-Disposition'] = 'attachment; filename=timetable%d_%d_%s.pdf' % (table_id + 1, view_year, ugettext(get_choice_display(SEMESTER_TYPES, view_semester)))
    activate(old_lang)

    return response


@login_required
def save_as_image(request):
    table_id = int(request.GET.get('id', 0))
    view_year = int(request.GET.get('view_year', settings.NEXT_YEAR))
    view_semester = int(request.GET.get('view_semester', settings.NEXT_SEMESTER))
    old_lang = request.session.get('django_language', 'ko')

    f = open(_get_image(_render_html(request)), 'rb')

    response = HttpResponse(FileWrapper(f), content_type='image/png')
    activate('en')
    response['Content-Disposition'] = 'attachment; filename=timetable%d_%d_%s.png' % (table_id + 1, view_year, ugettext(get_choice_display(SEMESTER_TYPES, view_semester)))
    activate(old_lang)

    return response

