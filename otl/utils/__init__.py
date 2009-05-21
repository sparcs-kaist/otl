# encoding: utf-8
from django.db import models
from django import forms
from django.core.cache import cache

def get_choice_display(choices, key):
	for item in choices:
		if item[0] == key:
			return item[1]
	return u'(None)'

def cache_with_default(key, default, timeout=300):
	"""
	cache.get() 메소드에도 default 인자가 있지만, 호출 당시 이미 evaluate되므로
	항상 다음과 같은 구조를 사용해야 한다.
	
	value = cache.get(key)
	if value is None:
		value = calculate()
		cache.set(key, value)
	
	그러나 Python에서 제공되는 lambda 함수를 사용하면 인자로 넘길 때 바로
	evaluate되지 않고 명시적으로 호출해야만 하므로 cache가 있는 경우 그냥
	무시하고 없는 경우에만 호출하여 default 인자를 바로 연산값으로 사용할
	경우 보다 간결한 코드로 표현할 수 있다.
	"""
	if not callable(default):
		raise TypeError('The argument default should be a callable, normally lambda function to work efficiently.')
	value = cache.get(key)
	if value is None:
		value = default()
		cache.set(key, value, timeout)
	return value

# MultiSelectField customization from http://www.djangosnippets.org/snippets/1200/
class MultiSelectFormField(forms.MultipleChoiceField):
	widget = forms.CheckboxSelectMultiple
	
	def __init__(self, *args, **kwargs):
		self.max_choices = kwargs.pop('max_choices', 0)
		super(MultiSelectFormField, self).__init__(*args, **kwargs)

	def clean(self, value):
		if not value and self.required:
			raise forms.ValidationError(self.error_messages['required'])
		if value and self.max_choices and len(value) > self.max_choices:
			raise forms.ValidationError(u'You must select a maximum of %s choice%s.'
					% (apnumber(self.max_choices), pluralize(self.max_choices)))
		return value

class MultiSelectField(models.Field):
	__metaclass__ = models.SubfieldBase

	def get_internal_type(self):
		return "CharField"

	def get_choices_default(self):
		return self.get_choices(include_blank=False)

	def _get_FIELD_display(self, field):
		value = getattr(self, field.attname)
		choicedict = dict(field.choices)

	def formfield(self, **kwargs):
		# don't call super, as that overrides default widget if it has choices
		defaults = {'required': not self.blank, 'label': self.verbose_name, 
					'help_text': self.help_text, 'choices':self.choices}
		if self.has_default():
			defaults['initial'] = self.get_default()
		defaults.update(kwargs)
		return MultiSelectFormField(**defaults)

	def get_db_prep_value(self, value):
		if isinstance(value, basestring):
			return value
		elif isinstance(value, list):
			return u','.join(value)

	def to_python(self, value):
		if isinstance(value, list):
			return value
		if value is None:
			return u''
		return value.split(u',')

	def contribute_to_class(self, cls, name):
		super(MultiSelectField, self).contribute_to_class(cls, name)
		if self.choices:
			func = lambda self, fieldname = name, choicedict = dict(self.choices):",".join([choicedict.get(value,value) for value in getattr(self,fieldname)])
			setattr(cls, 'get_%s_display' % self.name, func)

