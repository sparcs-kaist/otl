# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from otl.apps.common import SEMESTER_TYPES

class TakenLecture(models.Model):
    title = models.CharField(max_length=100)         # 과목명(국문)
    title_en = models.CharField(max_length=100)      # 과목명(영문)
    credit = models.IntegerField()                                  # 학점
    au = models.IntegerField()                                      # AU
    year = models.IntegerField()                                    # 개설년도
    semester = models.SmallIntegerField(choices=SEMESTER_TYPES)     # 개설학기 (1=봄, 2=여름, 3=가을, 4=겨울)
    type_one = models.CharField(max_length=12)                      # 과목구분1(국문)
    type_en_one = models.CharField(max_length=36)                   # 과목구분1(영문)
    type_two = models.CharField(max_length=12,null=True)                      # 과목구분2(국문)
    type_en_two = models.CharField(max_length=36,null=True)			# 과목구분2(영문)
    user = models.ForeignKey(User)         # 과목 들은 유저


class GradCredit(models.Model):
    mandantory_general = models.IntegerField()                      # 교양필수(학점)
    mandantory_general_au = models.IntegerField()                   # 교양필수(au)
    general_required = models.IntegerField()                        # 공통필수
    major_required_one = models.IntegerField()                          # 전공필수(주전)
    major_elective_one = models.IntegerField()                          # 전공선택(주전)
    major_required_two = models.IntegerField()                      # 전공필수(복부전)
    major_elective_two = models.IntegerField()                      # 전공선택(복부전)
    basic_required = models.IntegerField()                          # 기초필수
    basic_elective = models.IntegerField()                          # 기초선택
    social_elective = models.IntegerField()                         # 인문사회선택
    research = models.IntegerField()                                # 연구학점

class TakenLectureAdmin(admin.ModelAdmin):
    list_display = ('title','title_en','credit','au','year','semester','type_one','type_two','user')

class GradCreditAdmin(admin.ModelAdmin):
    list_display = ('mandantory_general','general_required','major_required_one','major_elective_one','major_required_two','major_elective_two','basic_required','basic_elective','social_elective','research')



admin.site.register(GradCredit, GradCreditAdmin)
admin.site.register(TakenLecture, TakenLectureAdmin)
