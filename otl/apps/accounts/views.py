# -*- coding: utf-8
from django.template import RequestContext
from django.http import *
from django.contrib import auth
from django.shortcuts import render_to_response
from django.contrib.admin.models import User
from django.contrib.auth.decorators import login_required
from otl.utils import cache_with_default
from otl.apps.timetable.models import Lecture
from otl.apps.favorites.models import CourseLink
from otl.apps.groups.models import GroupBoard
from otl.apps.calendar.models import Calendar, RepeatedSchedule, Schedule
from otl.apps.accounts.models import UserProfile, Department
from otl.apps.accounts.forms import LoginForm, ProfileForm
from otl.apps.common import *
import base64, hashlib, time, random, urllib, re

from django import template
template.add_to_builtins('django.templatetags.i18n')

from django.utils.translation import ugettext

def login(request):

    num_users = cache_with_default('stat.num_users', lambda: User.objects.count() - 1, 60)
    num_lectures = cache_with_default('stat.num_lectures', lambda: Lecture.objects.filter(year=settings.NEXT_YEAR, semester=settings.NEXT_SEMESTER).count(), 600)
    num_favorites = cache_with_default('stat.num_favorites', lambda: CourseLink.objects.count(), 60)
    num_schedules = cache_with_default('stat.num_schedules', lambda: Schedule.objects.filter(one_of=None).count() + RepeatedSchedule.objects.count(), 30)
    num_groups = cache_with_default('stat.num_groups', lambda: GroupBoard.objects.count(), 60)

    next_url = request.GET.get('next', '/')
    if request.method == 'POST':

        if not request.POST.has_key('agree'):
            # Do login process
            f = LoginForm(request.POST)
            if not f.is_valid():
                return render_to_response('login.html', {
                    'form_login': f,
                    'title': ugettext(u'로그인'),
                    'error': True,
                    'msg': ugettext(u'아이디/비밀번호를 모두 적어야 합니다.'),
                    'next': next_url,
                    'num_users': num_users,
                    'num_lectures': num_lectures,
                    'num_favorites': num_favorites,
                    'num_schedules': num_schedules,
                    'num_groups': num_groups,
                }, context_instance=RequestContext(request))

            try:
                user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
            except UnicodeEncodeError:
                return HttpResponseBadRequest('Bad Request')

            if user is None: # Login Failed
                return render_to_response('login.html', {
                    'form_login': f,
                    'title': ugettext(u'로그인'),
                    'error': True,
                    'msg': ugettext(u'로그인에 실패하였습니다.'),
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
                        'title': ugettext(u'로그인'),
                        'kuser_info': user.kuser_info,
                        'form_profile': ProfileForm(),
                        'next': next_url,
                    }, context_instance=RequestContext(request))
                else:
                    # Already existing user
                    if not user.is_superuser:
                        profile = UserProfile.objects.get(user=user)
                    # Create user's default system calendars if not exists
                    color = 1
                    for key, value in SYSTEM_CALENDAR_NAMES.iteritems():
                        try:
                            Calendar.objects.get(owner=user, system_id=key)
                        except Calendar.DoesNotExist:
                            c = Calendar()
                            c.owner = user
                            c.system_id = key
                            c.title = value
                            c.color = color
                            c.save()
                        color += 1
                    auth.login(request, user)
                    # If persistent login options is set, let the session expire after 2-weeks.
                    if request.POST.has_key('persistent_login'):
                        request.session.set_expiry(14*24*3600)
                    request.session['django_language'] = user.userprofile.language[:2]
                    return HttpResponseRedirect(next_url)
        else:
            # Show privacy agreement form after confirming this is a valid user in KAIST.
            if request.POST['agree'] == 'yes':
                user = User.objects.get(username = request.POST['username'])
                user.backend = 'otl.apps.accounts.backends.KAISTSSOBackend'

                # Create user's profile
                try:
                    profile = UserProfile.objects.get(user__exact = user)
                except UserProfile.DoesNotExist:
                    profile = UserProfile()
                profile.user = user
                profile.language = request.POST['language']
                try:
                    profile.department = Department.objects.get(id__exact=int(request.POST['department_no']))
                except:
                    profile.department = Department.objects.get(id__exact=0) # 찾을 수 없는 학과 사람은 일단 무학과로 등록
                profile.student_id = request.POST['student_id']
                profile.save()
                profile.favorite_departments.add(Department.objects.get(id=2044)) # 인문사회과학부는 기본으로 추가

                # Create user's default system calendars
                color = 1
                for key, value in SYSTEM_CALENDAR_NAMES.iteritems():
                    try:
                        Calendar.objects.get(owner=user, system_id=key)
                    except Calendar.DoesNotExist:
                        c = Calendar()
                        c.owner = user
                        c.system_id = key
                        c.title = value
                        c.color = color
                        c.save()
                    color += 1

                # Registration finished!
                auth.login(request, user)
                return HttpResponseRedirect(next_url)
            else:
                return HttpResponseNotAllowed(ugettext(u'개인정보 활용에 동의하셔야 서비스를 이용하실 수 있습니다. 죄송합니다.'))

    else:
        # Show login form for GET requests
        return render_to_response('login.html', {
            'title': ugettext(u'로그인'),
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
            msg = ugettext(u'사용자 정보가 변경되었습니다.')
            request.session['django_language'] = profile.language[:2]
            return HttpResponseRedirect('/accounts/myinfo/')
        else:
            msg = ugettext(u'올바르지 않은 입력입니다.')
            error = True
    else:
        # View my account information
        f = ProfileForm({
            'language': profile.language,
            'favorite_departments': [item.pk for item in profile.favorite_departments.all()],
        })
        msg = u''
    return render_to_response('accounts/myinfo.html', {
        'title': ugettext(u'내 계정'),
        'form_profile': f,
        'user_profile': profile,
        'department': profile.department.name if profile.department.name_en == None or request.session.get('django_language', 'ko') == 'ko' else profile.department.name_en,
        'error': error,
        'msg': msg,
        'lang' : request.session.get('django_language', 'ko'),
    }, context_instance=RequestContext(request))

def view(request, user_id):
    if request.user.is_authenticated():
        search = UserProfile.objects.filter(user__username__exact = user_id)
        if search:
            search_user = search[0]
            department = search_user.department.name if search_user.department.name_en == None or request.session.get('django_language', 'ko') == 'ko' else search_user.department.name_en
            first_name = search_user.user.first_name
            last_name = search_user.user.last_name
            return render_to_response('accounts/view.html', {
                'title': ugettext(u'다른 사람 정보 보기'),
                'department': department,
                'fname': first_name,
                'lname': last_name,
            }, context_instance=RequestContext(request))

    return HttpResponseRedirect('/')
