# -*- coding: utf-8
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
#from otl.apps.dictionary.models import Comment

class Department(models.Model):
    id = models.IntegerField(primary_key=True, help_text=u'세자리 또는 네자리의 숫자로 된 고유 ID')
    num_id = models.IntegerField(help_text=u'과목에서 prefix로 사용하는 숫자로 된 ID')
    code = models.CharField(max_length=5, help_text=u'과목에서 prefix로 사용하는 문자열로 된 ID')
    name = models.CharField(max_length=60)
    name_en = models.CharField(max_length=60, null=True)
    visible = models.BooleanField(default=True)

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
    score = models.IntegerField(default=0, null=False, blank=True)
    nickname = models.CharField(max_length=15, null=False, blank=True)
    like_list = models.ManyToManyField('dictionary.Comment', null=True, blank=True)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.user.username, self.student_id, self.department.code)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'department')

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(User, UserAdmin)

