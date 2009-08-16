# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from otl.apps.common import *

class CourseLink(models.Model):
    course_name = models.CharField(max_length=60)
    year = models.IntegerField(default=settings.CURRENT_YEAR)
    semester = models.SmallIntegerField(default=settings.CURRENT_SEMESTER, choices=SEMESTER_TYPES)
    url = models.URLField()
    favored_count = models.IntegerField(default=0)
    writer = models.ForeignKey(User, related_name='courselink_set')
    written = models.DateTimeField(auto_now_add=True)
    favored_by = models.ManyToManyField(User, related_name='favorite_set', blank=True)

class CourseLinkAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'year', 'semester', 'url', 'writer')
    ordering = ('-written',)

admin.site.register(CourseLink, CourseLinkAdmin)
