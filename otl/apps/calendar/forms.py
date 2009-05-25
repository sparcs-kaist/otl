# -*- encoding: utf8 -*-
from django import forms

SCHEDULE_TYPES = (
	('repeated', u'반복 일정'),
	('single', u'단독 일정'),
)

# TODO: refactor the following 2 forms?

class ScheduleForm(forms.Form):
	# TODO: support repeated schedule type also.
	type = forms.ChoiceField(label=u'형식', choices=SCHEDULE_TYPES, widget=forms.HiddenInput(), initial='single')
	summary = forms.CharField(label=u'제목', max_length=120)
	location = forms.CharField(label=u'장소', max_length=120, required=False)
	description = forms.CharField(label=u'설명', required=False)
	date = forms.DateField(label=u'날짜', input_formats=['%Y-%m-%d'])
	time_start = forms.IntegerField(widget=forms.HiddenInput())
	time_end = forms.IntegerField(widget=forms.HiddenInput())

	# TODO: validate the range of time_start, time_end?

class ScheduleModifyForm(forms.Form):
	id = forms.IntegerField(widget=forms.HiddenInput())
	summary = forms.CharField(label=u'제목', max_length=120)
	location = forms.CharField(label=u'장소', max_length=120, required=False)
	description = forms.CharField(label=u'설명', required=False)
	date = forms.DateField(label=u'날짜', input_formats=['%Y-%m-%d'])
	time_start = forms.IntegerField(widget=forms.HiddenInput())
	time_end = forms.IntegerField(widget=forms.HiddenInput())
