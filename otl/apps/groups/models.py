# encoding: utf8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from otl.apps.common import *

class GroupBoard(models.Model):
	group_name = models.CharField(max_length=60)
	comment = models.CharField(max_length=100)
	passwd = models.CharField(max_length=32)
	year = models.IntegerField()
	semester = models.SmallIntegerField(choices=SEMESTER_TYPES)
	maker = models.ForeignKey(User, related_name='groupboard_set')
	made = models.DateTimeField()
	group_in = models.ManyToManyField(User, related_name='group_set')

class GroupArticle(models.Model):
	group = models.ForeignKey(GroupBoard, related_name='article_set')
	tag = models.CharField(max_length=500)
	writer = models.ForeignKey(User, related_name='writer_set')
	written = models.DateTimeField()

class GroupBoardAdmin(admin.ModelAdmin):
	list_display = ('group_name', 'year', 'semester', 'maker')
	ordering = ('-made',)

admin.site.register(GroupBoard, GroupBoardAdmin)
