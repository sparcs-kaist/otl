# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from otl.apps.common import *
from otl.apps.timetable.models import Lecture

class Professor(models.Model):
    professor = models.CharField(max_length=100)            # 교수님 이름 (한글)
    professor_en = models.CharField(max_length=100, blank=True, null=True)  # 교수님 이름 (영문)
    prof_id = models.IntegerField()
    #department = models.ForeignKey(Department)              # 학과
    #code = models.CharField(max_length=10)                 # 교수님코드

class Course(models.Model):
    code = models.CharField(max_length=10)                  # 과목코드 (12.123 형식)
    #department = models.ForeignKey(Department)              # 학과
    #title = models.CharField(max_length=100)                # 과목이름(한글)
    #title_en = models.CharField(max_length=200)             # 과목이름(영문)
    #type = models.CharField(max_length=12)                  # 과목구분( 한글; '전필', '전선', '기필', ...)
    #type_en = models.CharField(max_length=36)               # 과목구분(영문; 'Major Required', 'Major Selective', ...)
    #professors = models.ManyToManyField(Professor)          # 교수님 (과목을 담당했던 교수님들)
    #lectures = models.ManyToManyField(Lecture)              # 개강 과목목록 (학기별 과목 연동)
    recent_lecture = models.ManyToManyField(Professor)
    recent_summary = models.ForeignKey(Lecture)
    score_average = models.SmallIntegerField(choices=SCORE_TYPES)
    load_average = models.SmallIntegerField(choices=LOAD_TYPES)
    gain_average = models.SmallIntegerField(choices=GAIN_TYPES)

    #summary = models.CharField(max_length=65536)            # 과목요약
    #prerequisite_courses = models.ManyToManyField('self')   # 선수과목
    #editor = models.ForeignKey(User, related_name='course_set') # 수정한 사람
    #edited_date = models.DateTimeField(auto_now=True)       # 마지막 수정일

class Summary(models.Model):
    summary = models.CharField(max_length=65536)
    writer = models.ForeignKey(User)
    written_date = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course)

class Comment(models.Model):
    course = models.ForeignKey(Course)                      # 과목
    lecture = models.ForeignKey(Lecture)                    # 시기+과목
    #professor = models.ForeignKey(Professor)               # 교수님
    #professor = models.CharField(max_length=100)            # 교수님
    #professor_en = models.CharField(max_length=100, blank=True, null=True) # 교수님 이름(영문)
    #semester = models.IntegerField()                        # 학기 (5자리, 앞의 4자리는 개설년도, 뒤의 1자리는 개설학기)

    writer = models.ForeignKey(User, related_name='comment_set') # 수정한 사람
    written_date = models.DateTimeField(auto_now=True)       # 마지막 수정일
    comment = models.CharField(max_length=65536)            # 코멘트
    load = models.SmallIntegerField(choices=LOAD_TYPES)                       # 로드
    score = models.SmallIntegerField(choices=SCORE_TYPES)                      # 학점
    gain = models.SmallIntegerField(choices=GAIN_TYPES)                       # 남는 거
    like = models.IntegerField(default=0)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('course', 'comment', 'load', 'score', 'gain')
    ordering = ('-written_date',)

admin.site.register(Comment, CommentAdmin)

class LectureRating(models.Model):
    course = models.ForeignKey(Course, related_name='rating_set')   # 과목
    lecture = models.ForeignKey(Lecture)                            # 과목 (분반 포함)
    number_of_students = models.IntegerField()                      # 평가자 수
    number_of_respondents = models.IntegerField()                   # 응답자 수
    rating = models.FloatField()                                    # 점수
    standard_deviation = models.FloatField()                        # 표준편
    # rated_contents =                                              # 평가 항목
    # rated_score =                                                 # 구체 점수

    def rate_of_responds(self):
        return str(100.0 * self.number_of_respondents / self.number_of_students) + "%"
