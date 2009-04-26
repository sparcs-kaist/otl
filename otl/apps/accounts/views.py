# encoding: utf-8
from django.template import RequestContext
from django.http import *
from django.contrib import auth
from django.shortcuts import render_to_response
from django.contrib.admin.models import User
from django.contrib.auth.decorators import login_required
from otl.apps.accounts.models import UserProfile, Department
from otl.apps.accounts.forms import LoginForm, ProfileForm
import base64, hashlib, time, random, urllib, re

def login(request):

	if request.method == 'POST':
		next_url = request.GET.get('next', '/')

		if not request.POST.has_key('agree'):
			# Do login process
			f = LoginForm(request.POST)
			if not f.is_valid():
				return render_to_response('login.html', {
					'form_login': f,
					'title': u'로그인',
					'error': True,
					'msg': u'아이디/비밀번호를 모두 적어야 합니다.',
				}, context_instance=RequestContext(request))

			user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])

			if user is None: # Login Failed
				return render_to_response('login.html', {
					'form_login': f,
					'title': u'로그인',
					'error': True,
					'msg': u'로그인에 실패하였습니다.',
				}, context_instance=RequestContext(request))
			else: # Login OK
				try:
					temp = user.first_login
				except AttributeError:
					user.first_login = False
				if user.first_login:
					# First Login
					return render_to_response('login_agreement.html', {
						'username': user.username,
						'title': u'로그인',
						'kuser_info': user.kuser_info,
						'form_profile': ProfileForm(),
					}, context_instance=RequestContext(request))
				else:
					# Already existing user
					if not user.is_superuser:
						profile = UserProfile.objects.get(user=user)
					auth.login(request, user)
					return HttpResponseRedirect(next_url)
		else:
			# Show privacy agreement form after confirming this is a valid user in KAIST.
			if request.POST['agree'] == 'yes':
				user = User.objects.get(username = request.POST['username'])
				user.backend = 'otl.apps.accounts.backends.KAISTSSOBackend'
				profile = UserProfile()
				profile.user = user
				profile.language = request.POST['language']
				profile.department = Department.objects.get(name__exact=request.POST['department'])
				profile.student_id = request.POST['student_id']
				profile.save()
				profile.favorite_departments.add(Department.objects.get(id=2044)) # 인문사회과학부는 기본으로 추가

				auth.login(request, user)
				return HttpResponseRedirect(next_url)
			else:
				return HttpResponseNotAllowed(u'개인정보 활용에 동의하셔야 서비스를 이용하실 수 있습니다. 죄송합니다.')

	else:
		# Show login form
		return render_to_response('login.html', {
			'title': u'로그인',
			'form_login': LoginForm(),
		}, context_instance=RequestContext(request))

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/')

@login_required
def myinfo(request):
	profile = UserProfile.objects.get(user=request.user)
	error = False
	if request.method == 'POST':
		# Modify my account information
		f = ProfileForm(request.POST)
		if f.is_valid():
			profile.language = f.cleaned_data['language']
			profile.favorite_departments = f.cleaned_data['favorite_departments']
			profile.save()
			msg = u'사용자 정보가 변경되었습니다.'
		else:
			msg = u'올바르지 않은 입력입니다.'
			error = True
	else:
		# View my account information
		f = ProfileForm({
			'language': profile.language,
			'favorite_departments': [item.pk for item in profile.favorite_departments.all()],
		})
		msg = u''
	return render_to_response('accounts/myinfo.html', {
		'title': u'내 계정',
		'form_profile': f,
		'user_profile': profile,
		'error': error,
		'msg': msg,
	}, context_instance=RequestContext(request))

