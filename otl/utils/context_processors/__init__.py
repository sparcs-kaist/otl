# -*- coding: utf-8
from django.conf import settings
from django.core.cache import cache
from otl.apps.common import *
from otl.apps.favorites.models import CourseLink
from datetime import date
from otl.apps.dictionary.views import _favorites_to_output,_taken_lectures_to_output
from otl.apps.accounts.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist

def globaltime(request):
    """서비스 전체에서 사용되는 기본 년도/학기 정보를 template 변수로 자동으로 포함시킨다."""
    return {
        'current_year': date.today().year,
        'current_semester': settings.CURRENT_SEMESTER,
        'current_semester_name': SEMESTER_TYPES[settings.CURRENT_SEMESTER][1],
        'next_year': settings.NEXT_YEAR,
        'next_semester': settings.NEXT_SEMESTER,
        'next_semester_name': SEMESTER_TYPES[settings.NEXT_SEMESTER][1],
    }

def myfavorites(request):
    """로그인한 사용자의 즐겨찾기 정보를 가져와 자동으로 포함시킨다."""
    if request.user.is_authenticated():
        favorites = CourseLink.objects.filter(year=settings.CURRENT_YEAR, semester=settings.CURRENT_SEMESTER, favored_by__exact=request.user)
        return {'myfavorites': favorites}
    else:
        return {'myfavorites': []}

def favorites(request):
    """dictionary의 즐겨찾기 정보를 가지고 있는다."""
    if request.user.is_authenticated():
        try: 
            favorite_list = _favorites_to_output(UserProfile.objects.get(user=request.user).favorite.all(), True, request.session.get('django_language','ko'))
        except ObjectDoesNotExist:
            favorite_list = []
    else:
        favorite_list = []
    
    return { 'favorite' : favorite_list }

def taken_lecture_list(request):
    """dictionary의 들었던 과목 정보를 가지고 있는다."""
    if request.user.is_authenticated():
        try:
            take_lecture_list = UserProfile.objects.get(user=request.user).take_lecture_list.order_by('-year', '-semester')
            take_year_list = take_lecture_list.values('year', 'semester').distinct()
            separate_list = []
            result = []
            for lecture in take_lecture_list:
                if len(separate_list)==0:
                    separate_list.append(lecture)
                    continue
                if lecture.year!=separate_list[0].year or lecture.semester!=separate_list[0].semester :
                    result.append(_taken_lectures_to_output(request.user, separate_list, request.session.get('django_language','ko')))
                    separate_list = []
                separate_list.append(lecture)
            result.append(_taken_lectures_to_output(request.user, separate_list, request.session.get('django_language','ko')))
        except ObjectDoesNotExist:
            result = []
            take_year_list = []
    else:
        take_year_list = []
        result = []

    result = zip(take_year_list,result)
    return { 'lecture_list' : result }
