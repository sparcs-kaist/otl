# encoding: utf-8
from django import forms
from otl.apps.common import *
from otl.apps.accounts.models import Department

class LoginForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.Form):
	favorite_departments = forms.ModelMultipleChoiceField(queryset=Department.objects.all(), required=False, label=u'관심 학과 :', help_text=u'최대 3개까지 선택하실 수 있습니다.')
	language = forms.ChoiceField(choices=LANGUAGES, label=u'Language :')

	def clean_favorite_departments(self):
		data = self.cleaned_data['favorite_departments']
		if len(data) > 3:
			raise forms.ValidationError(u'관심 학과의 최대 허용 개수를 초과하였습니다.')
		return data
