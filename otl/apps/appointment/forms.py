# encoding: utf-8
from django import forms

class CreateStep1Form(forms.Form):
	summary = forms.CharField(max_length=120, label=u'약속 요약')
