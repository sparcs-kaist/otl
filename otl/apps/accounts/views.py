# encoding: utf-8
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.shortcuts import render_to_response
from otl.apps.accounts.models import UserProfile
from otl.apps.accounts.forms import LoginForm
import base64, hashlib, time, random, urllib, re

def login(request):

	if request.method == 'POST':
		# Do login process
		f = LoginForm(request.POST)

		print auth
		user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])

		if user is None: # Login Failed
			return render_to_response('login.html', {
				'form_login': f,
				'msg': u'로그인에 실패하였습니다.',
			}, context_instance=RequestContext(request))
		else: # Login Ok
			profile = UserProfile.objects.get(user=user)
			auth.login(request, user)
			return render_to_response('test.html', {
				'userid': user.username,
				'student_id': profile.student_id,
				'department': profile.department,
				'fullname': '%s %s' % (user.first_name, user.last_name),
			}, context_instance=RequestContext(request))
		
	else:
		# Show login form
		return render_to_response('login.html', {
			'form_login': LoginForm(),
		}, context_instance=RequestContext(request))

