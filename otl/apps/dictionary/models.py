# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from otl.apps.common import *
from otl.apps.timetable.models import Lecture
from otl.apps.accounts.models import Department

class Professor(models.Model):
    professor_name = models.CharField(max_length=100)            # 교수님 이름 (한글)
    professor_name_en = models.CharField(max_length=100, blank=True, null=True)  # 교수님 이름 (영문)
    professor_id = models.IntegerField()

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor', 'professor_en', 'professor_id')

class Course(models.Model):
    old_code = models.CharField(max_length=10)                  # 과목코드 (ABC123 형식)
    department = models.ForeignKey(Department)
    professors = models.ManyToManyField(Professor)
    type = models.CharField(max_length=12)
    type_en = models.CharField(max_length=36)
    title = models.CharField(max_length=100)
    title_en = models.CharField(max_length=200)
    score_average = models.FloatField()
    load_average = models.FloatField()
    gain_average = models.FloatField()

class CourseAdmin(admin.ModelAdmin):
    list_display = ('old_code', 'department', 'type', 'title', 'score_average', 'load_average', 'gain_average')

class Summary(models.Model):
    summary = models.CharField(max_length=65536)
    prerequisite = models.CharField(max_length=512)
    writer = models.ForeignKey(User)
    written_datetime = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course)

class SummaryAdmin(admin.ModelAdmin):
    list_display = ('summary', 'writer', 'written_datetime', 'course')

class Comment(models.Model):
    course = models.ForeignKey(Course)                      # 과목
    lecture = models.ForeignKey(Lecture, null=True, blank=True)  # 시기+과목

    writer = models.ForeignKey(User, related_name='comment_set') # 수정한 사람
    written_datetime = models.DateTimeField(auto_now=True)       # 마지막 수정일
    comment = models.CharField(max_length=65536)            # 코멘트
    load = models.SmallIntegerField(choices=LOAD_TYPES)                       # 로드
    score = models.SmallIntegerField(choices=SCORE_TYPES)                      # 학점
    gain = models.SmallIntegerField(choices=GAIN_TYPES)                       # 남는 거
    like = models.IntegerField(default=0)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('course', 'comment', 'load', 'score', 'gain')
    ordering = ('-written_datetime',)

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

class LectureRatingAdmin(admin.ModelAdmin):
    list_display = ('course', 'lecture', 'number_of_students', 'number_of_respondents', 'rating', 'standard_deviation')

class AlreadyWrittenError(Exception):
    pass


admin.site.register(Comment, CommentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(LectureRating, LectureRatingAdmin)
