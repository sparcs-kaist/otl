# encoding: utf8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Department(models.Model):
	num_id = models.IntegerField()
	code = models.CharField(max_length=5)
	name = models.CharField(max_length=60)
	name_en = models.CharField(max_length=60, null=True)

	def __unicode__(self):
		return u'%s(%d) "%s"' % (self.code, self.num_id, self.name)

class DepartmentAdmin(admin.ModelAdmin):
	ordering = ('num_id',)
	list_display = ('num_id', 'code', 'name')
admin.site.register(Department, DepartmentAdmin)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	student_id = models.CharField(max_length=10)
	language = models.CharField(max_length=15)
	department = models.ForeignKey('Department')
	favorite_departments = models.ManyToManyField('Department', related_name='favoredby_set')

	def __unicode__(self):
		return u'%s %s (%s)' % (self.user.username, self.student_id, self.department.code)

class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'student_id', 'department')
admin.site.register(UserProfile, UserProfileAdmin)
