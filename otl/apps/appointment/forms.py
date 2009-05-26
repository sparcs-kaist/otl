# encoding: utf-8
from django import forms
from otl.apps.appointment.models import APPOINTMENT_OPERATIONS
from otl.utils.forms import MultipleDateTimeRangeField

class CreateForm(forms.Form):
	summary = forms.CharField(max_length=120, label=u'약속 요약')
	time_ranges = MultipleDateTimeRangeField()

class ChangeForm(forms.Form):
	submit_operation = forms.ChoiceField(choices=APPOINTMENT_OPERATIONS)
	time_ranges = MultipleDateTimeRangeField()
