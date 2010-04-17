# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from otl.apps.common import *
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import *

class Course(models.Model):
    code = models.CharField(max_length=10)                  # 과목코드 (12.123 형식)
    department = models.ForeignKey(Department)              # 학과
    title = models.CharField(max_length=100)                # 과목이름(한글)
    title_en = models.CharField(max_length=200)             # 과목이름(영문)
    type = models.CharField(max_length=12)                  # 과목구분( 한글; '전필', '전선', '기필', ...)
    type_en = models.CharField(max_length=36)               # 과목구분(영문; 'Major Required', 'Major Selective', ...)
    audience = models.IntegerField(choices=AUDIENCE_TYPES)  # 학년구분
    credit = models.IntegerField(default=3)                 # 학점
    num_classes = models.IntegerField(default=3)            # 강의 시간
    num_labs = models.IntegerField(default=0)               # 실험 시간
    credit_au = models.IntegerField(default=0)              # AU
    limit = models.IntegerField(default=0)                  # 인원제한
    is_english = models.BooleanField()                      # 영어강의 여부
    deleted = models.BooleanField(default=False)            # 과목이 닫혔는지 여부
    summary = models.CharField(max_length=65536)                            # 과목요약
    prerequisite_courses = models.ManyToManyField('self')    # 선수과목
    lectures = models.ManyToManyField(Lecture)              # 개강 과목목록 (학기별 과목 연동)
    
class LectureRating(models.Model):
    course = models.ForeignKey(Course, related_name='rating_set')
    lecture = models.ForeignKey(Lecture)
    number_of_students = models.IntegerField()
    number_of_respondents = models.IntegerField()
    rating = models.FloatField()
    standard_deviation = models.FloatField()

    def rate_of_responds(self):
        return str(100.0 * self.number_of_respondents / self.number_of_students) + "%"

class CourseComment(models.Model):
    writer = models.ForeignKey(User, related_name='comment_set')
    written = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course)
    lecture = models.ForeignKey(Lecture)
    comment = models.CharField(max_length=4096)
    load = models.NullBooleanField()
    score = models.NullBooleanField()
    gain = models.NullBooleanField()

    def load_str(self):
        if self.load == False:
            return '쉬움'
        elif self.load == None:
            return '무난'
        else:
            return '힘듬'

    def score_str(self):
        if self.score == False:
            return '박함'
        elif self.score == None:
            return '무난'
        else:
            return '후함'

    def gain_str(self):
        if self.gain == False:
            return '없음'
        elif self.gain == None:
            return '있음'
        else:
            return '많음'


    
class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ('writer', 'written', 'load', 'score', 'gain', 'lecture', 'comment')
    ordering = ('-written',)

admin.site.register(CourseComment, CourseCommentAdmin)

