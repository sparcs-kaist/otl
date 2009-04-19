# encoding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from otl.apps.accounts.models import Department
from otl.utils import MultiSelectField, get_choice_display
from otl.apps.common import *

class Calendar(models.Model):
	owner = models.ForeignKey(User)
	title = models.CharField(max_length=60)
	enabled = models.BooleanField(default=True)

	def __unicode__(self):
		return u'%s\'s %s' % (self.title, self.owner.username)

class CalendarAdmin(admin.ModelAdmin):
	list_display = ('owner', 'title', 'enabled')
	ordering = ('owner', 'title')

class RepeatedSchedule(models.Model):
	belongs_to = models.ForeignKey(Calendar)
	rule = models.IntegerField(choices=SCHEDULE_REPEAT_TYPES)
	weekdays = MultiSelectField(choices=WEEKDAYS, max_length=20, blank=True)
	day_of_months = MultiSelectField(choices=MONTHDAYS, max_length=80, blank=True)
	date_begin = models.DateField(null=True, blank=True)
	date_end = models.DateField(null=True, blank=True)
	time_begin = models.TimeField(null=True, blank=True)
	time_end = models.TimeField(null=True, blank=True)

	def __unicode__(self):
		if self.rule == 1: # 매주 일정
			rules = u', '.join(map(lambda day: get_choice_display(WEEKDAYS, int(day)), self.weekdays))
		elif self.rule == 2: # 매월 일정
			rules = u'일, '.join(self.day_of_months) + u'일'
		else:
			rules = u'(unrecognized repetition rule)'
		try:
			date_range = u'%s - %s' % (self.date_begin.strftime('%m/%d'), self.date_end.strftime('%m/%d'))
		except:
			date_range = u'제한 없음'
		try:
			time_range = u'%s - %s' % (self.time_begin.strftime('%H:%M'), self.time_end.strftime('%H:%M'))
		except:
			time_range = u'종일'
		return u'%s 반복(%s): %s @ %s' % (self.get_rule_display(), date_range, time_range, rules)

class RepeatedScheduleAdmin(admin.ModelAdmin):
	list_display = ('belongs_to', '__unicode__')
	list_links = ('__unicode__',)

class Schedule(models.Model):
	belongs_to = models.ForeignKey(Calendar)
	one_of = models.ForeignKey(RepeatedSchedule, null=True, blank=True)
	summary = models.CharField(max_length=120)
	location = models.CharField(max_length=120)
	date = models.DateField()
	begin = models.TimeField()
	end = models.TimeField()
	description = models.TextField(blank=True)

class ScheduleAdmin(admin.ModelAdmin):
	pass

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(RepeatedSchedule, RepeatedScheduleAdmin)
admin.site.register(Schedule, ScheduleAdmin)

