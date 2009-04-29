# encoding: utf-8
from django.template import RequestContext
from django.http import *
from django.core.cache import cache
from django.contrib import auth
from django.shortcuts import render_to_response
from django.contrib.admin.models import User
from django.contrib.auth.decorators import login_required
from otl.apps.timetable.models import Lecture
from otl.apps.favorites.models import CourseLink
from otl.apps.groups.models import GroupBoard
from otl.apps.calendar.models import Schedule
from otl.apps.accounts.models import UserProfile, Department
from otl.apps.accounts.forms import LoginForm, ProfileForm
import base64, hashlib, time, random, urllib, re

def login(request):

	# TODO: check if default value is evaluated before method calling.
	num_users = cache.get('stat.num_users', User.objects.count() - 1)
	num_lectures = cache.get('stat.num_lectures', Lecture.objects.filter(year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER).count())
	num_favorites = cache.get('stat.num_favorites', CourseLink.objects.count())
	num_schedules = cache.get('stat.num_schedules', Schedule.objects.count())
	num_groups = cache.get('stat.num_groups', GroupBoard.objects.count())

	cache.set('stat.num_users', num_users, 60)
	cache.set('stat.num_lectures', num_lectures, 600)
	cache.set('stat.num_favorites', num_favorites, 60)
	cache.set('stat.num_schedules', num_schedules, 20)
	cache.set('stat.num_groups', num_groups, 60)

	next_url = request.GET.get('next', '/')
	if request.method == 'POST':

		if not request.POST.has_key('agree'):
			# Do login process
			f = LoginForm(request.POST)
			if not f.is_valid():
				return render_to_response('login.html', {
					'form_login': f,
					'title': u'로그인',
					'error': True,
					'msg': u'아이디/비밀번호를 모두 적어야 합니다.',
					'next': next_url,
					'num_users': num_users,
					'num_lectures': num_lectures,
					'num_favorites': num_favorites,
					'num_schedules': num_schedules,
					'num_groups': num_groups,
				}, context_instance=RequestContext(request))

			user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])

			if user is None: # Login Failed
				return render_to_response('login.html', {
					'form_login': f,
					'title': u'로그인',
					'error': True,
					'msg': u'로그인에 실패하였습니다.',
					'next': next_url,
					'num_users': num_users,
					'num_lectures': num_lectures,
					'num_favorites': num_favorites,
					'num_schedules': num_schedules,
					'num_groups': num_groups,
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
						'next': next_url,
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
			'next': next_url,
			'num_users': num_users,
			'num_lectures': num_lectures,
			'num_favorites': num_favorites,
			'num_schedules': num_schedules,
			'num_groups': num_groups,
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

