# encoding: utf-8
from django import forms
from otl.utils.forms import MultipleDateTimeRangeField

class CreateForm(forms.Form):
	summary = forms.CharField(max_length=120, label=u'약속 요약')
	time_ranges = MultipleDateTimeRangeField()
