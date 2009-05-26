# -*- encoding: utf8 -*-
from django import forms
from otl.apps.common import *

# TODO: refactor the following 2 forms?

class ScheduleForm(forms.Form):
	summary = forms.CharField(label=u'제목', max_length=120)
	location = forms.CharField(label=u'장소', max_length=120, required=False)
	description = forms.CharField(label=u'설명', required=False)
	date = forms.DateField(label=u'날짜', input_formats=['%Y-%m-%d'])

	# 일일 일정인 경우에는 시간 정의 필요 없음.
	time_start = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	time_end = forms.IntegerField(widget=forms.HiddenInput(), required=False)

	# TODO: validate the range of time_start, time_end?

class ScheduleCreateForm(ScheduleForm):
	# TODO: support repeated schedule type also.
	type = forms.ChoiceField(label=u'형식', choices=SCHEDULE_TYPES, widget=forms.HiddenInput(), initial='single')
	range = forms.ChoiceField(label=u'일일/종일', choices=SCHEDULE_RANGES)

class ScheduleModifyForm(ScheduleForm):
	id = forms.IntegerField(widget=forms.HiddenInput())

class ScheduleListForm(forms.Form):
	date_start = forms.DateField(input_formats=['%Y-%m-%d'])
	date_end = forms.DateField(input_formats=['%Y-%m-%d'])
