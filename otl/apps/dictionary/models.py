# -*- coding: utf-8
from django.db import models
from django.db.models import Avg
from django.contrib import admin
from django.contrib.auth.models import User
from otl.apps.common import *
from otl.apps.timetable.models import Lecture
from otl.apps.accounts.models import Department

class Professor(models.Model):
    professor_name = models.CharField(max_length=100)            # 교수님 이름 (한글)
    professor_name_en = models.CharField(max_length=100, blank=True, null=True)  # 교수님 이름 (영문)
    professor_id = models.IntegerField()

class ProfessorInfor(models.Model):
    major = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    homepage = models.CharField(max_length=200)
    writer = models.ForeignKey(User)
    written_datetime = models.DateTimeField(auto_now=True)
    professor = models.ForeignKey(Professor)

class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor_name', 'professor_name_en', 'professor_id')

class ProfessorInforAdmin(admin.ModelAdmin):
    list_display = ('professor','major','email','homepage','writer', 'written_datetime')
    ordering = ('-id',)

class Course(models.Model):
# *이 붙은 항목은 Lecture가 업데이트될때 함께 업데이트 되어야 할 것
    old_code = models.CharField(max_length=10)                  # 과목코드 (ABC123 형식) *
    department = models.ForeignKey(Department)                  # 가장 최근의 department *
    professors = models.ManyToManyField(Professor)              # 맡았던 교수들 *
    type = models.CharField(max_length=12)                      # 가장 최근의 type *
    type_en = models.CharField(max_length=36)                   # 가장 최근의 type_en *
    title = models.CharField(max_length=100)                    # 가장 최근의 title *
    title_en = models.CharField(max_length=200)                 # 가장 최근의 title_en *
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
    list_display = ('summary', 'prerequisite', 'writer', 'written_datetime', 'course')

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
    like_list = models.ManyToManyField(User, related_name='comment_likelist', null=True)

    @staticmethod
    def course_average(courses):
        comments = Comment.objects.filter(course__in=courses)
        if len(comments) == 0:
            average = {'avg_score':0, 'avg_gain':0, 'avg_load':0}
        else:
            average = comments.aggregate(avg_score=Avg('score'),avg_gain=Avg('gain'),avg_load=Avg('load'))
        return average

class CommentAdmin(admin.ModelAdmin):
    list_display = ('course', 'comment', 'load', 'score', 'gain')
    ordering = ('-id',)

class Score(models.Model):
    composition = models.FloatField()
    understand = models.FloatField()
    creative = models.FloatField()
    support = models.FloatField()

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('composition','understand','creative','support')

class LectureRating(models.Model):
    lecture = models.ForeignKey(Lecture)                            # 과목 (분반 포함)
    number_of_students = models.IntegerField()                      # 평가자 수
    number_of_respondents = models.IntegerField()                   # 응답자 수
    number_of_effective_respondents = models.IntegerField()         # 유효응답자 수
    rating = models.FloatField()                                    # 점수
    standard_deviation = models.FloatField()                        # 표준편가
    rated_score = models.ForeignKey(Score, null=True, blank=True)   # 강의평가 항목별 점수

    def rate_of_responds(self):
        return str(100 * self.number_of_respondents / self.number_of_students) + "%"

    def rate_of_effective_responds(self):
        return str(100 * self.number_of_effective_respondents / self.number_of_students) + "%"

class LectureSummary(models.Model):
    homepage = models.CharField(max_length=200)
    main_material = models.CharField(max_length=512)
    sub_material = models.CharField(max_length=512)
    writer = models.ForeignKey(User)
    written_datetime = models.DateTimeField(auto_now=True)
    lecture = models.ForeignKey(Lecture)

class LectureRatingAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'number_of_students', 'number_of_respondents', 'number_of_effective_respondents','rating', 'standard_deviation', 'rated_score')

class LectureSummaryAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'homepage', 'main_material', 'sub_material', 'writer', 'written_datetime')
    ordering = ('-id',)

class AlreadyWrittenError(Exception):
    pass

admin.site.register(Professor, ProfessorAdmin)
admin.site.register(ProfessorInfor, ProfessorInforAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Summary, SummaryAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(LectureRating, LectureRatingAdmin)
admin.site.register(LectureSummary, LectureSummaryAdmin)
