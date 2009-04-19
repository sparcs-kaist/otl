# encoding: utf-8
from django.template import RequestContext
from django.http import *
from django.contrib import auth
from django.shortcuts import render_to_response
from django.contrib.admin.models import User
from otl.apps.accounts.models import UserProfile, Department
from otl.apps.accounts.forms import LoginForm
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
					'msg': u'아이디/비밀번호를 모두 적어야 합니다.',
				}, context_instance=RequestContext(request))

			user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])

			if user is None: # Login Failed
				return render_to_response('login.html', {
					'form_login': f,
					'msg': u'로그인에 실패하였습니다.',
				}, context_instance=RequestContext(request))
			else: # Login OK
				if user.first_login:
					# First Login
					return render_to_response('login_agreement.html', {
						'username': user.username,
						'kuser_info': user.kuser_info,
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

				auth.login(request, user)
				return HttpResponseRedirect(next_url)
			else:
				return HttpResponseNotAllowed(u'개인정보 활용에 동의하셔야 서비스를 이용하실 수 있습니다. 죄송합니다.')

	else:
		# Show login form
		return render_to_response('login.html', {
			'form_login': LoginForm(),
		}, context_instance=RequestContext(request))

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/')
