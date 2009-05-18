# encoding: utf-8
from django.db import models
from django.core.exceptions import *
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from otl.apps.accounts.models import Department
from otl.utils import MultiSelectField, get_choice_display
from otl.apps.common import *
import Sybase, MySQLdb

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

def fetch_assignments(student_id):
	"""
	Moodle DB에 접속하여 해당 학번의 학생이 듣고 있는 과목들에 대한 과제 정보를 가져온다.
	"""
	if not isinstance(student_id, int):
		raise TypeError('student_id must be an integer.')

	# TODO: cache!!

	taking_courses = []
	try:
		scholar_db = Sybase.connect(settings.SCHOLARDB_HOST, settings.SCHOLARDB_USER, settings.SCHOLARDB_PASSWORD, settings.SCHOLARDB_NAME)
	except:
		raise DatabaseError('Cannot access the scholar database!')
	cursor = scholar_db.cursor()
	cursor.execute("SELECT a.subject_no, l.old_no FROM view_OTL_attend a, view_OTL_lecture l
	WHERE a.student_no = %d AND a.lecture_year = %d AND a.lecture_term = %d
	AND a.lecture_year = l.lecture_year AND a.lecture_term = l.lecture_term AND a.subject_no = l.subject_no AND a.lecture_class = l.lecture_class AND a.dept_id = l.dept_id",
		(student_id, settings.CURRENT_YEAR, settings.CURRENT_SEMESTER))
	rows = cursor.fetchall()
	for row in rows:
		taking_courses.append(row[1])
	cursor.close()
	scholar_db.close()

	assignments = []
	try:
		moodle_db = MySQLdb.connect(host=settings.MOODLEDB_HOST, user=settings.MOODLEDB_USER, password=settings.MOODLEDB_PASSWORD, db=settings.MOODLEDB_NAME, use_unicode=True, charset='utf8')
	except:
		raise DatabaseError('Cannot access the moodle database!')
	cursor = moodle_db.cursor()
	for course_no in taking_courses:
		# TODO: implement!
		cursor.execute("SELECT * FROM mdl_assignment WHERE ...")
		rows = cursor.fetchall()
		for row in rows:
			pass
	moodle_db.close()

	return assignments

admin.site.register(Calendar, CalendarAdmin)
admin.site.register(RepeatedSchedule, RepeatedScheduleAdmin)
admin.site.register(Schedule, ScheduleAdmin)

