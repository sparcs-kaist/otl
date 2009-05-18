# -*- encoding: utf-8 -*-
from django import template
from otl.apps.common import *
from otl.utils import get_choice_display

register = template.Library()

@register.filter
def term2str(value):
	return get_choice_display(SEMESTER_TYPES, value)
