# encoding: utf-8
from django.conf import settings
from otl.apps.common import *

def globaltime(request):
	"""서비스 전체에서 사용되는 기본 년도/학기 정보를 template 변수로 자동으로 포함시킨다."""
	return {
		'current_year': settings.CURRENT_YEAR,
		'current_semester': SEMESTER_TYPES[settings.CURRENT_SEMESTER][1],
		'next_year': settings.NEXT_YEAR,
		'next_semester': SEMESTER_TYPES[settings.NEXT_SEMESTER][1],
	}
