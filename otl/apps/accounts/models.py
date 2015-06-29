# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Department(models.Model):
    id = models.IntegerField(primary_key=True, help_text=u'세자리 또는 네자리의 숫자로 된 고유 ID',db_index=True)
    num_id = models.CharField(max_length=4, help_text=u'과목에서 prefix로 사용하는 문자로 된 ID',db_index=True)
    code = models.CharField(max_length=5, help_text=u'과목에서 prefix로 사용하는 문자열로 된 ID',db_index=True)
    name = models.CharField(max_length=60,db_index=True)
    name_en = models.CharField(max_length=60, null=True,db_index=True)
    visible = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s(%s) "%s"' % (self.code, self.num_id, self.name)

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
    nickname = models.CharField(max_length=15, null=False, blank=True)
    take_lecture_list = models.ManyToManyField('timetable.Lecture', related_name='take_lecture_list', null=True)
    favorite=models.ManyToManyField('dictionary.Course', related_name='favorite_user', null=True)
    calendar_id = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=30,null=True,blank=True)
    grad_credit = models.OneToOneField('credit.GradCredit')
    minor = models.ForeignKey('Department',related_name='minor_user',null=True)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.user.username, self.student_id, self.department.code)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'department', 'nickname')

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(User, UserAdmin)

