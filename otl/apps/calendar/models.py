# -*- coding: utf-8
from django.db import models, DatabaseError
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture
from otl.utils.models import MultiSelectField
from otl.utils import get_choice_display
from otl.apps.common import *
from datetime import datetime

class Calendar(models.Model):
    owner = models.ForeignKey(User)
    system_id = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=60)
    color = models.IntegerField()
    enabled = models.BooleanField(default=True)

    """
    시스템 상에서 사용자가 생성될 때 기본으로 추가되는 시스템 Calendar 종류는 다음과 같다.
    Calendar 이름은 가입시 설정하는 언어에 따라 생성되며 나중에 사용자가 변경할 수 있다.
    각각은 뒤에 붙어있는 system_id 값을 가지며 이 값이 비어있지 않은 경우 사용자가 임의로 삭제할 수 없다.
    (사용자가 생성하는 달력은 해당 값을 비워두어 구분하는데, 아직 사용자 달력 생성은 지원하지 않음)

    - 학과시간표 / timetable : 강의 시간, 시험 및 과제 일정
    - 약속 / appointment : 약속 잡기 기능으로부터 추가된 약속 일정들
    - 개인일정 / private : 개인용으로만 사용되는 일정(시스템에 의한 추가/삭제 없음)

    시스템 Calendar라 하더라도 개인이 스스로 일정을 지우거나 삭제할 수 있다.

    @see login() at otl/apps/accounts/views.py
    """

    def __unicode__(self):
        return u'%s\'s %s' % (self.title, self.owner.username)

class CalendarAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'enabled')
    ordering = ('owner', 'title')

class RepeatedSchedule(models.Model):
    # TODO: 전체 일정 개수를 셀 때, repeated schedule + schedule NOT a part of repeated schedule로 계산
    belongs_to = models.ForeignKey(Calendar)
    rule = models.IntegerField(choices=SCHEDULE_REPEAT_TYPES)
    summary = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    weekdays = MultiSelectField(choices=WEEKDAYS, max_length=20, blank=True)
    day_of_months = MultiSelectField(choices=MONTHDAYS, max_length=80, blank=True)
    # TODO: lazy-creation of schedule items
    #       처음 반복일정을 생성할 때 그에 해당하는 Schedule 오브젝트를 한번에
    #       생성하지 않고, 해당 오브젝트가 들어있어야 하는 날짜 범위에 대한 요청이
    #       들어온 경우에만 생성한다. (1달치 정도는 그냥 해도 될 듯.)
    date_begin = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    time_begin = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        rule = u''
        if self.rule == 1: # 매주 일정
            rule = u'매주'
            rules = u', '.join(map(lambda day: get_choice_display(WEEKDAYS, int(day)), self.weekdays))
        elif self.rule == 2: # 매월 일정
            rule = u'매월'
            rules = u'일, '.join(self.day_of_months) + u'일'
        else:
            rule = u'?'
            rules = u'(unrecognized repetition rule)'
        try:
            date_range = u'%s - %s' % (self.date_begin.strftime('%m/%d'), self.date_end.strftime('%m/%d'))
        except:
            date_range = u'제한 없음'
        try:
            time_range = u'%s - %s' % (self.time_begin.strftime('%H:%M'), self.time_end.strftime('%H:%M'))
        except:
            time_range = u'종일'
        return u'%s 반복(%s): %s @ %s' % (rule, date_range, time_range, rules)

class RepeatedScheduleAdmin(admin.ModelAdmin):
    list_display = ('belongs_to', '__unicode__')
    list_links = ('__unicode__',)

class Schedule(models.Model):
    belongs_to = models.ForeignKey(Calendar)
    one_of = models.ForeignKey(RepeatedSchedule, null=True, blank=True)
    summary = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    range = models.SmallIntegerField(choices=SCHEDULE_RANGES, default=0)
    date = models.DateField()
    begin = models.TimeField(blank=True, null=True)
    end = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True)

    def separate_from_repeated(self):
        self.summary = self.one_of.summary
        self.description = self.one_of.description
        self.location = self.one_of.location
        self.one_of = None
        self.save()
    
    def __unicode__(self):
        return u'%d-%d %d:%d-%d:%d "%s"' % (self.date.month, self.date.day, self.begin.hour, self.begin.minute, self.end.hour, self.end.minute, self.summary)

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('belongs_to', 'one_of', '__unicode__')
    list_links = ('__unicode__',)

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(RepeatedSchedule, RepeatedScheduleAdmin)
admin.site.register(Schedule, ScheduleAdmin)

def get_system_calendar(user, system_id):
    try:
        c = Calendar.objects.get(owner=user, system_id=system_id)
    except Calendar.DoesNotExist:
        c = Calendar()
        c.owner = user
        c.title = SYSTEM_CALENDAR_NAMES[system_id]
        c.system_id = system_id
        c.color = 1
        c.enabled = True
        c.save()
    return c

def is_in_current_semester(someday):
    start = settings.SEMESTER_RANGES[(settings.CURRENT_YEAR, settings.CURRENT_SEMESTER)][0]
    end = settings.SEMESTER_RANGES[(settings.CURRENT_YEAR, settings.CURRENT_SEMESTER)][1]
    return someday >= start and someday <= end

def is_in_exam_periods(someday):
    exam_periods = settings.EXAM_PERIODS[(settings.CURRENT_YEAR, settings.CURRENT_SEMESTER)]
    for p in exam_periods:
        if someday >= p[0] and someday <= p[1]:
            return True
    return False

def is_holiday(someday):
    if someday.month == 3 and someday.day == 1: # 삼일절
        return True
    if someday.month == 5 and someday.day == 5: # 어린이날
        return True
    if someday.month == 10 and someday.day == 3: # 개천절
        return True
    # TODO: add more holidays!
    # TODO: 강성훈의 Python 음력 변환기를 사용하여 추석, 설, 초파일도 자동 처리?
    
    return False

def fetch_assignments(student_id):
    """
    Moodle DB에 접속하여 해당 학번의 학생이 듣고 있는 과목들에 대한 과제 정보를 가져온다.
    """
    if not isinstance(student_id, int):
        raise TypeError('student_id must be an integer.')

    # TODO: cache!!
    taking_courses = fetch_taking_courses(student_id)
    assignments = []
    try:
        import MySQLdb
        moodle_db = MySQLdb.connect(host=settings.MOODLEDB_HOST, user=settings.MOODLEDB_USER, passwd=settings.MOODLEDB_PASSWORD, db=settings.MOODLEDB_NAME, use_unicode=True, charset='utf8')
    except ImportError:
        raise DatabaseError('MySQLdb module is not installed!')
    except:
        raise DatabaseError('Cannot access the moodle database!')
    cursor = moodle_db.cursor()
    for lecture in taking_courses:
        cursor.execute("""SELECT c.shortname, a.name, a.description, a.format, a.assignmenttype, a.timedue, a.timeavailable, a.grade, a.timemodified
        FROM mdl_assignment a, mdl_course c WHERE c.id = a.course AND c.shortname LIKE '%s%%'""" % lecture.old_code) 
        # TODO: moodle 조교와 협의하여 shortname에 과목 코드뿐만 아니라 분반, 개설년도/개설학기 정보도 포함시켜 정확한 과목 matching이 이루어지게 한다.
        #       현재 같은 과목이라도 분반에 따라 moodle을 이용하기도 하고 이용하지 않기도 하는 경우가 있어 과목코드만으로 가져오면 실제로 자기하고는
        #       상관 없는 과제 정보를 얻어오는 경우가 있다.
        rows = cursor.fetchall()
        for row in rows:
            # Convert time
            assignment = [item for item in row]
            assignment[5] = datetime.fromtimestamp(assignment[5])
            assignment[6] = datetime.fromtimestamp(assignment[6])
            assignment[8] = datetime.fromtimestamp(assignment[8])
            assignments.append(assignment)
    cursor.close()
    moodle_db.close()

    return assignments

def fetch_taking_courses(student_id):
    """
    학사 DB에 접속하여 해당 학번의 학생이 듣고 있는 과목 정보를 가져온다.
    """
    if not isinstance(student_id, int):
        raise TypeError('student_id must be an integer.')

    # TODO: cache!!
    taking_courses = []
    try:
        import Sybase
        scholar_db = Sybase.connect(settings.SCHOLARDB_HOST, settings.SCHOLARDB_USER, settings.SCHOLARDB_PASSWORD, settings.SCHOLARDB_NAME)
    except ImportError:
        raise DatabaseError('Sybase module is not installed!')
    except:
        raise DatabaseError('Cannot access the scholar database!')
    cursor = scholar_db.cursor()
    cursor.execute("""SELECT l.subject_no, l.old_no, l.dept_id, l.lecture_class FROM view_OTL_attend a, view_OTL_lecture l
    WHERE a.student_no = %d AND a.lecture_year = %d AND a.lecture_term = %d
    AND a.lecture_year = l.lecture_year AND a.lecture_term = l.lecture_term AND a.subject_no = l.subject_no AND a.lecture_class = l.lecture_class AND a.dept_id = l.dept_id"""
        % (student_id, settings.CURRENT_YEAR, settings.CURRENT_SEMESTER))
    rows = cursor.fetchall()
    try:
        for row in rows:
            taking_courses.append(Lecture.objects.get(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, code=row[0], department__id=row[2], class_no=row[3].strip()))
    except Lecture.DoesNotExist:
        raise DatabaseError('Matching lecture(%s) which a student(%d) is taking was not found! Check scholar-db synchronization.' % (row[0], student_id))
    cursor.close()
    scholar_db.close()

    return taking_courses

