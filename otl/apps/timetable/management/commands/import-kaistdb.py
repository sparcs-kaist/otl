# encoding: utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from otl.apps.accounts.models import Department
from optparse import make_option
import sys, getpass, re
import Sybase

class Command(BaseCommand):
	option_list = BaseCommand.option_list + (
		make_option('--host', dest='host', help=u'Specifies server address.'),
		make_option('--user', dest='user', help=u'Specifies user name to log in.'),
		make_option('--encoding', dest='encoding', help=u'Sepcifies character encoding to decode strings from database. (default is cp949)', default='cp949'),
	)
	help = u'Imports KAIST scholar database.'
	args = u'--host=143.248.X.Y:PORT --user=USERNAME'

	def handle(self, *args, **options):
		rx_dept_code = re.compile(ur'([a-zA-Z]+)(\d+)')
		host = options.get('host', None)
		user = options.get('user', None)
		encoding = options.get('encoding', 'cp949')
		try:
			password = getpass.getpass()
		except KeyboardInterrupt:
			print
			return

		try:
			db = Sybase.connect(host, user, password, 'scholar')
		except Sybase.DatabaseError:
			print>>sys.stderr, u'Connection failed. Check username and password.'
			return
		c = db.cursor()

		c.execute('SELECT * FROM view_OTL_lecture WHERE lecture_year = %d AND lecture_term = %d' % (settings.NEXT_YEAR, settings.NEXT_SEMESTER))
		rows = c.fetchall()
		departments = {}

		for row in rows:
			myrow = []
			for elem in row:
				if isinstance(elem, str):
					elem = elem.decode(encoding)
				myrow.append(elem)

			# Extract department info.
			lecture_no = myrow[2]
			lecture_code = myrow[20]
			department_no = int(lecture_no[0:2])
			department_code = rx_dept_code.match(lecture_code).group(1)

			if not departments.has_key(department_no):
				departments[department_no] = (department_code, myrow[5], myrow[6])
				print u'Added department: %s(%d): %s' % (department_code, department_no, myrow[5])

			# Extract lecture info.
			print u'Importing %s: %s [%s]...' % (lecture_code, myrow[7], myrow[3].strip())

		print u'\nTotal number of departments : %d' % len(departments)
		print u'Total number of lectures : %d' % len(rows)
		print u'\nSaving...'

		# Saving department info.
		for key, value in departments.iteritems():
			item = Department()
			item.num_id = key 
			item.code = value[0]
			item.name = value[1]
			item.name_en = value[2]
			item.save()

		print u'Saving complete.'
		c.close()
		db.close()
