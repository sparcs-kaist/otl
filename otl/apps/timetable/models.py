# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from otl.apps.accounts.models import Department
from otl.apps.common import *
from datetime import date, time
import re
from django.db.models.signals import post_save, post_delete

def on_change_relation(sender, **kwargs):
    if sender == Timetable:
        instance = kwargs['instance']
        instance.lecture.update_num_people()

post_save.connect(on_change_relation)
post_delete.connect(on_change_relation)

class Lecture(models.Model):
    """특정 년도·학기에 개설된 과목 instance를 가리키는 모델"""
    code = models.CharField(max_length=10)                  # 과목코드 (12.123 형식)
    old_code = models.CharField(max_length=10, db_index=True)              # 과목코드 (ABC123 형식)
    year = models.IntegerField()                            # 개설년도 (4자리 숫자)
    semester = models.SmallIntegerField(choices=SEMESTER_TYPES) # 개설학기 (1=봄, 2=여름, 3=가을, 4=겨울)
    department = models.ForeignKey(Department)              # 학과
    class_no = models.CharField(max_length=4, blank=True)   # 분반
    title = models.CharField(max_length=100, db_index=True)                # 과목이름 (한글)
    title_en = models.CharField(max_length=200, db_index=True)             # 과목이름 (영문)
    type = models.CharField(max_length=12)                  # 과목구분 (한글; '전필', '전선', '기필', ...)
    type_en = models.CharField(max_length=36)               # 과목구분 (영문; 'Major Required', 'Major Elective', ...)
    audience = models.IntegerField(choices=AUDIENCE_TYPES)  # 학년구분
    credit = models.IntegerField(default=3)                 # 학점
    num_classes = models.IntegerField(default=3)            # 강의 시간
    num_labs = models.IntegerField(default=0)               # 실험 시간
    credit_au = models.IntegerField(default=0)              # AU
    limit = models.IntegerField(default=0)                  # 인원제한
    num_people = models.IntegerField(default=0, blank=True, null=True)  #신청인원
    professor = models.CharField(max_length=100, db_index=True)            # 교수님 이름 (한글)
    professor_en = models.CharField(max_length=100, blank=True, null=True, db_index=True)  # 교수님 이름 (영문)
    notice = models.CharField(max_length=200, blank=True, null=True)        # 비고
    is_english = models.BooleanField()                      # 영어강의 여부
    deleted = models.BooleanField(default=False)            # 과목이 닫혔는지 여부
    rating = models.ForeighKey(LectureRating)

    timetable_relation = models.ManyToManyField(User, through='Timetable', null=True, blank=True)

    def __unicode__(self):
        return u'%s (%d:%s) %s' % (self.code, self.year, self.get_semester_display(), self.title)

    def update_num_people(self):
        self.num_people = len(set(self.timetable_relation.all()))
        self.save()
        return self.num_people
    
    def check_classtime_overlapped(self, another_lecture):
        """이 과목과 주어진 다른 과목의 강의 시간 중 겹치는 것이 있는지 검사한다."""
        my_times = self.classtime_set.all()
        their_times = another_lecture.classtime_set.all()

        for mt in my_times:
            for tt in their_times:
                if not (mt.end <= tt.begin or mt.begin >= tt.end) and mt.day == tt.day:
                    return True
        return False

    def dictionary_url(self):
        return 'dictionary/' + self.code

    class Meta:
        unique_together = ('code', 'year', 'semester', 'department', 'class_no')

class LectureAdmin(admin.ModelAdmin):
    list_display = ('code', 'year', 'semester', 'department', 'class_no', 'title', 'professor', 'type', 'audience', 'credit', 'credit_au', 'limit')
    ordering = ('-year', '-semester', 'code')

class ExamTime(models.Model):
    """Lecture에 배정된 시험 시간."""
    lecture = models.ForeignKey(Lecture)
    day = models.SmallIntegerField(choices=WEEKDAYS)    # 시험 요일
    begin = models.TimeField()              # hh:mm 형태의 시험 시작 시간 (24시간제)
    end = models.TimeField()                # hh:mm 형태의 시험 종료 시간 (24시간제)

    def get_begin_numeric(self):
        """0시 0분을 기준으로 분 단위로 계산된 시작 시간을 반환한다."""
        t = self.begin.hour * 60 + self.begin.minute
        if t % 30 != 0:
            t = t + (30 - (t % 30))
        return t

    def get_end_numeric(self):
        """0시 0분을 기준으로 분 단위로 계산된 종료 시간을 반환한다."""
        t = self.end.hour * 60 + self.end.minute
        if t % 30 != 0:
            t = t + (30 - (t % 30))
        return t

    def __unicode__(self):
        return u'[%s] %s, %s-%s' % (self.lecture.code, self.get_day_display(), self.begin.strftime('%H:%M'), self.end.strftime('%H:%M'))

class ExamTimeAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'day', 'begin', 'end')
    ordering = ('lecture',)

class ClassTime(models.Model):
    """Lecture에 배정된 강의 시간. 보통 하나의 Lecture가 여러 개의 강의 시간을 가진다."""
    lecture = models.ForeignKey(Lecture)            
    day = models.SmallIntegerField(choices=WEEKDAYS)
    begin = models.TimeField()
    end = models.TimeField()
    type = models.CharField(max_length=1, choices=CLASS_TYPES)
    building = models.CharField(max_length=10, blank=True, null=True)   # 건물 고유ID (잘 사용되지 않음)
    room = models.CharField(max_length=60, blank=True, null=True)       # 호실 (잘 사용되지 않음)
    room_ko = models.CharField(max_length=60, blank=True, null=True)    # 수업 장소 (한글)
    room_en = models.CharField(max_length=60, blank=True, null=True)    # 수업 장소 (영문)
    unit_time = models.SmallIntegerField(blank=True, null=True)         # 수업 교시

    def get_begin_numeric(self):
        """0시 0분을 기준으로 분 단위로 계산된 시작 시간을 반환한다."""
        t = self.begin.hour * 60 + self.begin.minute
        if t % 30 != 0:
            t = t + (30 - (t % 30))
        return t

    def get_end_numeric(self):
        """0시 0분을 기준으로 분 단위로 계산된 종료 시간을 반환한다."""
        t = self.end.hour * 60 + self.end.minute
        if t % 30 != 0:
            t = t + (30 - (t % 30))
        return t
    
    def get_location(self):
        if self.room is None:
            return u'%s' % (self.room_ko)
        try:
            int(self.room)
            return u'%s %s호' % (self.room_ko, self.room)
        except ValueError:
            return u'%s %s' % (self.room_ko, self.room)
    
    def get_location_en(self):
        if self.room is None:
            return u'%s' % (self.room_en)
        try:
            int(self.room)
            return u'%s %s' % (self.room_en, self.room)
        except ValueError:
            return u'%s %s' % (self.room_en, self.room)

    @staticmethod
    def numeric_time_to_str(numeric_time):
        return u'%s:%s' % (numeric_time // 60, numeric_time % 60)
    
    @staticmethod
    def numeric_time_to_obj(numeric_time):
        return time(hour = numeric_time // 60, minute = numeric_time % 60)

    def __unicode__(self):
        return u'[%s] %s, %s-%s @%s' % (self.lecture.code, self.get_day_display(), self.begin, self.end, self.room_ko)

class ClassTimeAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'day', 'begin', 'end', 'room_ko')
    ordering = ('lecture',)

class Syllabus(models.Model):
    """Lecture에 대한 강의계획서 정보. 첨부파일로만 나오고 비어있는 경우도 있음."""
    lecture = models.ForeignKey(Lecture)
    professor_info = models.CharField(max_length=60)            # 교수님 정보
    abstract = models.TextField(blank=True)                     # 요약 정보
    evaluation = models.TextField(blank=True)                   # 평가 방법
    plan = models.TextField(blank=True)                         # 강의 계획
    materials = models.TextField(blank=True)                    # 교재
    etc = models.TextField(blank=True)                          # 기타
    url = models.URLField(blank=True)                           # 과목 홈페이지
    attachment = models.CharField(max_length=260, blank=True)   # 첨부파일 이름

    def __unicode__(self):
        return u'%s (%s)' % (self.lecture.code, self.professor_info)

class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'professor_info', 'abstract', 'url', 'attachment')
    ordering = ('lecture',)

# TODO: 수강신청 현황 View에 대응하는 Table


class Timetable(models.Model):
    user = models.ForeignKey(User)
    lecture = models.ForeignKey(Lecture)
    year = models.IntegerField()
    semester = models.IntegerField()
    table_id = models.IntegerField()

    def __unicode__(self):
        return u'%s\'s %s in table [%d]' % (self.user.username, self.lecture.code, self.table_id)

    class Meta:
        unique_together = (('user', 'lecture', 'year', 'semester', 'table_id'),)

class TimetableAdmin(admin.ModelAdmin):
    list_display = ('user', 'lecture', 'year', 'semester', 'table_id')
    ordering = ('user', 'year', 'semester', 'table_id')

class OverlappingTimeError(Exception):
    pass

admin.site.register(Lecture, LectureAdmin)
admin.site.register(ExamTime, ExamTimeAdmin)
admin.site.register(ClassTime, ClassTimeAdmin)
admin.site.register(Syllabus, SyllabusAdmin)
admin.site.register(Timetable, TimetableAdmin)
# vim: set ts=4 sts=4 sw=4 et:
