# -*- coding: utf-8

import os, tempfile
from django.shortcuts import render_to_response
from django.db.models import Count
from django.db import IntegrityError
from django.http import *
from django.template import RequestContext
from django.utils import simplejson as json
from django.conf import settings
from django.core.exceptions import *
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from otl.utils import respond_as_attachment
from otl.utils.decorators import login_required_ajax
from otl.apps.common import *
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ExamTime, ClassTime, Syllabus, Timetable, OverlappingTimeError
from StringIO import StringIO

def index(request):

    # Read the current user's timetable.
    if request.user.is_authenticated():
        my_lectures = [_lectures_to_output(Lecture.objects.filter(year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER, timetable__user=request.user, timetable__table_id=id), False) for id in xrange(0,3)]
    else:
        my_lectures = [[], [], []]
    if settings.DEBUG:
        my_lectures_output = json.dumps(my_lectures, indent=4, ensure_ascii=False)
    else:
        my_lectures_output = json.dumps(my_lectures, ensure_ascii=False, sort_keys=False, separators=(',',':'))
    
    # Delete the timetable item if the corresponding lecture is marked as deleted.
    # However, we already added this item to my_lectures to notify the user at least once.
    if request.user.is_authenticated():
        for lecture in Lecture.objects.filter(deleted=True, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER):
            Timetable.objects.filter(user=request.user, lecture=lecture).delete()

    return render_to_response('timetable/index.html', {
        'section': 'timetable',
        'title': u'모의시간표',
        'departments': Department.objects.filter(visible=True).order_by('name'),
        'my_lectures': my_lectures_output,
        'lecture_list': _lectures_to_output(_search(dept=u'2044', type=u'전체보기'))
    }, context_instance=RequestContext(request))

def search(request):
    try:
        # Convert QueryDict to a normal python dict.
        q = {}
        for key, value in request.GET.iteritems():
            q[str(key)] = value
        # Cache using search parameters
        cache_key = 'timetable-search-cache:' + ':'.join(['%s=%s' % (key, value) for key, value in q.iteritems()])
        output = cache.get(cache_key)
        if output is None:
            output = _lectures_to_output(_search(**q))
            cache.set(cache_key, output, 3600)
        return HttpResponse(output)
    except ValidationError:
        return HttpResponseBadRequest()

@login_required_ajax
def add_to_timetable(request):
    user = request.user
    table_id = request.GET.get('table_id', None)
    lecture_id = request.GET.get('lecture_id', None)
    
    lectures = []
    try:
        lecture = Lecture.objects.get(pk=lecture_id)
        lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
        for existing_lecture in lectures:
            if existing_lecture.check_classtime_overlapped(lecture):
                raise OverlappingTimeError()
            # We don't check overlapped exam times.
        timetable = Timetable(user=user, lecture=lecture, year=lecture.year, semester=lecture.semester, table_id=table_id)
        timetable.save()

        lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST'
    except OverlappingTimeError:
        result = 'OVERLAPPED'
    except IntegrityError:
        result = 'DUPLICATED'
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'data': _lectures_to_output(lectures, False),
    }, ensure_ascii=False, indent=4))

@login_required_ajax
def delete_from_timetable(request):
    user = request.user
    table_id = request.GET.get('table_id', None)
    lecture_id = request.GET.get('lecture_id', None)

    lectures = []
    try:
        if lecture_id is None:
            Timetable.objects.filter(user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER, table_id=table_id).delete()
        else:
            lecture = Lecture.objects.get(pk=lecture_id)
            Timetable.objects.get(user=user, lecture=lecture, year=lecture.year, semester=lecture.semester, table_id=table_id).delete()

        lectures = Lecture.objects.filter(timetable__table_id=table_id, timetable__user=user, year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER)
        result = 'OK'
    except ObjectDoesNotExist:
        result = 'NOT_EXIST'
    except:
        return HttpResponseServerError()

    return HttpResponse(json.dumps({
        'result': result,
        'data': _lectures_to_output(lectures, False),
    }, ensure_ascii=False, indent=4))

@login_required_ajax
def view_timetable(request):
    user = request.user
    table_id = request.GET.get('table_id', None)

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
        'data': _lectures_to_output(lectures, False),
    }, ensure_ascii=False, indent=4))


# -- Private functions --

def _search(**conditions):
    department = conditions.get('dept', None)
    year = conditions.get('year', settings.NEXT_YEAR)
    semester = conditions.get('term', settings.NEXT_SEMESTER)
    type = conditions.get('type', None)
    day_begin = conditions.get('start_day', None)
    day_end = conditions.get('end_day', None)
    time_begin = conditions.get('start_time', None)
    time_end = conditions.get('end_time', None)

    # This query requires Django 1.1 or newer.
    lectures = Lecture.objects.annotate(num_classtimes=Count('classtime')).filter(year=year, semester=semester, num_classtimes__gt=0)
    
    try:
        if time_end != None and day_end != None and int(time_end) == 24*60:
            # 24:00가 종료시간인 경우 처리
            day_end = int(day_end)
            if day_end < 6:
                day_end += 1
            time_end = 0
        if department == u'-1' and type == u'전체보기':
            raise ValidationError()
        if department != None and department != u'-1':
            lectures = lectures.filter(department__id__exact=int(department))
        if type != None and type != u'전체보기':
            lectures = lectures.filter(type__exact=type)
        if day_begin != None and day_end != None and time_begin != None and time_end != None:
            if day_begin == day_end:
                lectures = lectures.filter(classtime__day__exact=int(day_begin),
                                           classtime__begin__gte=ClassTime.numeric_time_to_obj(int(time_begin)),
                                           classtime__end__lte=ClassTime.numeric_time_to_obj(int(time_end)))
            else:
                lectures = lectures.filter(classtime__day__gte=int(day_begin), classtime__day__lte=int(day_end),
                                           classtime__begin__gte=ClassTime.numeric_time_to_obj(int(time_begin)),
                                           classtime__end__lte=ClassTime.numeric_time_to_obj(int(time_end)))
    except (TypeError, ValueError):
        raise ValidationError()

    return lectures.filter(deleted=False).order_by('type', 'code').distinct()

def _lectures_to_output(lectures, conv_to_json=True):
    all = []
    for lecture in lectures:
        try:
            exam = lecture.examtime_set.get() # 첫번째 항목만 가져옴
        except:
            exam = None
        room = ClassTime.objects.filter(lecture=lecture, type__exact='l')
        if room.count() > 0:
            room = room[0].get_location()
        else:
            room = ''
        item = {
            'id': lecture.id,
            'year': lecture.year,
            'term': lecture.semester,
            'dept': lecture.department.name,
            'classification': lecture.type,
            'course_no': lecture.old_code,
            'class': lecture.class_no,
            'code': lecture.code,
            'title': lecture.title,
            'lec_time': lecture.num_classes,
            'lab_time': lecture.num_labs,
            'credit': lecture.credit,
            'au': lecture.credit_au,
            'fixed_num': lecture.limit,
            'classroom': room,
            'deleted': lecture.deleted,
            'prof': lecture.professor,
            'times': [{'day': schedule.day, 'start': schedule.get_begin_numeric(), 'end': schedule.get_end_numeric(), 'classroom': schedule.room_ko, 'type': schedule.get_type_display()} for schedule in lecture.classtime_set.all()],
            'remarks': u'영어강의' if lecture.is_english else u'',
            'examtime': {'day': exam.day, 'start': exam.get_begin_numeric(), 'end': exam.get_end_numeric()} if exam != None else None,
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

@login_required
def print_as_pdf(request):
    table_id = request.GET.get('id', 0)
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
    c.drawCentredString(page_width / 2, page_height - margin_y + 12, u'%(year)d년 %(semester)s학기 시간표' % {
        'year': settings.NEXT_YEAR,
        'semester': SEMESTER_TYPES[settings.NEXT_SEMESTER - 1][1],
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

    # Draw the actual timetable entries
    def get_box_position(day, time_begin, time_end):
        left = margin_x + timelabels_width + (column_width * day)
        bottom = page_height - (margin_y + header_height) - (row_height * ((time_end - 480) / 30.0))
        return left, bottom, column_width, row_height * ((time_end - time_begin) / 30.0)

    c.setDash([], 0)
    c.setLineWidth(0.12)
    my_lectures = Lecture.objects.filter(year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER, timetable__user=request.user, timetable__table_id=table_id)
    for lecture in my_lectures:
        for classtime in lecture.classtime_set.all():
            left, bottom, width, height = get_box_position(classtime.day, classtime.get_begin_numeric(), classtime.get_end_numeric())
            top = bottom + height
            c.setFillColorRGB(0.92, 0.92, 0.92)
            c.roundRect(left, bottom, width, height, 4.0, 1, 1)
            c.setFillColorRGB(0, 0, 0)
            c.setFont(sanserif_bold_name, 9)
            offset = height / 2.0
            c.drawCentredString(left + width / 2, bottom + offset + 4, lecture.title)
            c.setFont(sanserif_name, 9)
            c.drawCentredString(left + width / 2, bottom + offset - row_height + 4, classtime.get_location())

    # Save and transfer.
    c.showPage()
    c.save()
    response = respond_as_attachment(request, temp_path, 'Timetable.pdf', True)
    os.remove(temp_path)
    return response

