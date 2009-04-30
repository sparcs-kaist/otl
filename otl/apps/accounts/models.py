# encoding: utf8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Department(models.Model):
	id = models.IntegerField(primary_key=True, help_text=u'세자리 또는 네자리의 숫자로 된 고유 ID')
	num_id = models.IntegerField(help_text=u'과목에서 prefix로 사용하는 숫자로 된 ID')
	code = models.CharField(max_length=5, help_text=u'과목에서 prefix로 사용하는 문자열로 된 ID')
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

class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'first_name', 'last_name')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(User, UserAdmin)

def get_dept_from_deptname(name):
	"""
	A mapping function from string names to department objects with handling some exceptional cases.
	"""
	try:
		return Department.objects.get(name__exact=name)
	except Department.DoesNotExist:
		if name == u'기계공학전공':
			name = u'기계공학과'
			return Department.objects.get(name__exact=name)
		elif name == u'학과없음':
			return Department.objects.get(id__exact=10000)
	
	raise Department.DoesNotExist('Cannot match the department name (%s)' % name.encode('utf8').encode('hex'))
