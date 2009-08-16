# -*- coding: utf-8 -*-

import sys, textwrap
from optparse import make_option
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import *
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, Timetable


class Command(BaseCommand):
	option_list = BaseCommand.option_list + (
		make_option('--old-dept', dest='old_dept', help=u'Indicates the deprecated department. (Use the id value)'),
		make_option('--new-dept', dest='new_dept', help=u'Indicates the new target department. (Use the id value)'),
		make_option('--dry-run', dest='dry_run', action='store_true', help=u'If given, it will not do the migration actually, but only virtually and show the expected result.', default=False),
	)
	help = textwrap.dedent(u"""\
	Migrates all timetable entries according to department changes.
	IMPORTANT: See the source code (apps/timetable/management/commands/migrate_department.py)
	for detailed assumptions required for this operation.""")
	args = u'--old-dept=ID --new-dept=ID'

	def handle(self, *args, **options):
		# 기본 가정 :
		#   1. 이전 학과의 과목 정보를 가지고 있고, 동시에 새 학과의 과목 정보도 등록된 상황
		#   2. 이전 학과와 새 학과의 과목들의 시간표가 변경되지 않음 (학과 이름만 바뀐 상황)
		try:
			old_dept = Department.objects.get(id=options.get('old_dept', None))
		except Department.DoesNotExist:
			print>>sys.stderr, u'Could not retreive the old department given. See help for usage.'
			return
		try:
			new_dept = Department.objects.get(id=options.get('new_dept', None))
		except Department.DoesNotExist:
			print>>sys.stderr, u'Could not retreive the new department given. See help for usage.'
			return
		dry_run = options.get('dry_run', False)

		old_lectures = Lecture.objects.filter(department=old_dept)

		for old_lecture in old_lectures:
			old_timetable_entries = Timetable.objects.filter(lecture=old_lecture)
			try:
				new_lecture = Lecture.objects.get(
					department=new_dept,
					code=old_lecture.code,
					year=old_lecture.year,
					semester=old_lecture.semester,
					class_no=old_lecture.class_no,
				)
			except Lecture.DoesNotExist:
				print>>sys.stderr, u'Cannot find the correspoding lecture of %s in the new department! So let the timetable entry as it was.' % old_lecture
			else:
				if dry_run:
					# Show the changes row by row.
					for entry in old_timetable_entries:
						print u'Timetable entry #%(entry_id)d: %(old_lecture)s is rewritten to %(new_lecture)s' % {
							'entry_id': entry.id,
							'old_lecture': old_lecture,
							'new_lecture': new_lecture,
						}
				else:
					# Update all corresponding entries at once.
					old_timetable_entries.update(lecture=new_lecture)

				# IMPROTANT: Timetable model 외에 Lecture를 참조하는 model이 추가로 존재하면 거기서도 똑같이 처리해야 함.

		# We don't delete the old entries because it should show "deprecated" message to the user.

