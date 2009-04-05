# encoding: utf8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class CourseLink(models.Model):
	course_code = models.CharField(max_length=10)
	course_name = models.CharField(max_length=60)
	year = models.IntegerField()
	semester = models.SmallIntegerField()
	url = models.URLField()
	favored_count = models.IntegerField()
	writer = models.ForeignKey(User, related_name='courselink_set')
	written = models.DateTimeField() # written, last_updated는 관습적으로 작성/수정 시간을 표현하는 데 사용됨
	favored_by = models.ManyToManyField(User, related_name='favorite_set', blank=True ) #TODO : 과목명이 Null인 경우에 Contraints걸어 줘야됨

class CourseLinkAdmin(admin.ModelAdmin):
	list_display = ('course_code', 'course_name', 'year', 'semester', 'url', 'writer')
	ordering = ('-written',)

admin.site.register(CourseLink, CourseLinkAdmin)
