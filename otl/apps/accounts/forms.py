# encoding: utf-8
from django import forms
from otl.apps.common import *
from otl.apps.accounts.models import Department

class LoginForm(forms.Form):
	username = forms.CharField(max_length=30, label=u'Portal ID')
	password = forms.CharField(widget=forms.PasswordInput, label=u'비밀번호')
	persistent_login = forms.BooleanField(required=False, label=u'자동 로그인', help_text=u'2주 동안 로그인 상태를 유지합니다.<br/>공용컴퓨터에서는 사용하지 마세요.')

class ProfileForm(forms.Form):
	favorite_departments = forms.ModelMultipleChoiceField(queryset=Department.objects.all(), required=False, label=u'관심 학과 :', help_text=u'최대 3개까지 선택하실 수 있습니다. (Ctrl키를 누르고 클릭하세요.)')
	language = forms.ChoiceField(choices=LANGUAGES, label=u'Language :')

	def clean_favorite_departments(self):
		data = self.cleaned_data['favorite_departments']
		if len(data) > 3:
			raise forms.ValidationError(u'관심 학과의 최대 허용 개수를 초과하였습니다.')
		return data
