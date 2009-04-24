# encoding: utf-8
from django.conf import settings
from otl.apps.common import *
from datetime import date

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
