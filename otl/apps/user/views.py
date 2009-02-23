# encoding: utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response
from otl.apps.user.forms import LoginForm
import base64, hashlib, time, random

def login(request):
	step = request.GET.get('step', 1)

	if step == 1:
		# Show login form

		return render_to_response('login.html', {
			'form_login': LoginForm(),
		}, context_instance=RequestContext(request))

	elif step == 2:
		# Validate input and pass over to addr.kaist.ac.kr (KAIST-SSO)

		f = LoginForm(request.POST)
		if f.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			s = hashlib.sha256()
			s.update(time.time() + ':' + random.randint(1,9999999))
			token = s.hexdigest()
			request.session['token'] = token
			host = request.META['HTTP_HOST']
			return render_to_response('login_portal.html', {
				'token': token,
				'username_b64': base64.b64encode(username),
				'password_b64': base64.b64encode(password),
				'host': host,
			}, context_instance=RequestContext(request))
		else:
			return render_to_response('login.html', {
				'form_login': f,
				'message': u'ID/비밀번호를 모두 입력하세요.',
			}, context_instance=RequestContext(request))

	elif step == 3:
		# Check if whether login was successful or not.

		my_token = request.session.get('token', 'X')
		their_token = request.GET.get('token', 'Y')
		if my_token != their_token:
			# Token mismatch
			return render_to_response('login.html', {
				'form_login': LoginForm(),
				'msg': u'잘못된 접근입니다.',
			}, contenxt_instance=RequestContext(request))
		else:
			try:
				# Retrieve user information finally.
				id = request.POST['uid']
				department = request.POST['ku_departmentname'].decode('cp949')
				fullname = '%s %s' %
						   (request.POST['sn'].decode('cp949'), request.POST['givenname'].decode('cp949'))
				# TODO: call auth.login() to make use of Django user session.
				return render_to_response('test.html', {
					'uid': id,
					'username': '',
					'department': department,
					'fullname': fullname,
				}, context_instance=RequestContext(request))
			except KeyError:
				return render_to_response('login.html', {
					'form_login': LoginForm(),
					'msg': u'로그인에 실패하였습니다.',
				}, contenxt_instance=RequestContext(request))

