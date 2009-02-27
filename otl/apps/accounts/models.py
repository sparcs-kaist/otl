# encoding: utf8
from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
	num_id = models.IntegerField()
	code = models.CharField(max_length=5)
	name = models.CharField(max_length=60)

	def __unicode__(self):
		return u'%s(%d) "%s"' % (self.code, self.num_id, self.name)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	student_id = models.CharField(max_length=10)
	language = models.CharField(max_length=15)
	department = models.ForeignKey('Department')
	favorite_departments = models.ManyToManyField('Department', related_name='favoredby_set')

	def __unicode__(self):
		return u'%s %s (%s)' % (self.user.username, self.student_id, self.department.code)

