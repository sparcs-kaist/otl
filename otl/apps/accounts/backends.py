# encoding: utf-8
from django.contrib import auth
from django.contrib.auth.models import User
from otl.apps.accounts.models import UserProfile, Department
import urllib, urllib2
import base64
import re

_rx_name_val = re.compile(r"name=([^ ]*) value='([^']*)'")

class KAISTSSOBackend:
	
	def authenticate(self, username=None, password=None):

		request_info = [
			('isenc', 't'),
			('b001', base64.b64encode(username)),
			('b002', base64.b64encode(password)),
			('b003', 'givenname'),
			('b003', 'sn'),
			('b003', 'uid'),
			('b003', 'mail'),
			('b003', 'ku_where'),
			('b003', 'ku_departmentname'),
			('b003', 'ku_socialName'),
			('b003', 'ku_where'),
			('b003', 'ku_regno1'),
			#('b003', 'ku_regno2'), # 주민등록번호 뒷자리는 생략하고 받지 않음
			('b003', 'ku_dutyName'),
			('b003', 'ku_dutyCode'),
			('b003', 'ku_socialName'),
			('b003', 'ku_socialcode'),
			('b003', 'ku_titleCode'),
			('b003', 'ku_status'),
		]

		request = urllib2.Request('http://addr.kaist.ac.kr/auth/authenticator')
		username_enc = base64.b64encode(username)
		password_enc = base64.b64encode(password)

		# TODO: register otl.kaist.ac.kr to IT service department.
		request.add_header('Referer', 'http://moodle.kaist.ac.kr')
		request.add_data(urllib.urlencode(request_info))

		try:
			ret = urllib2.urlopen(request).read()
			ret = urllib.unquote_plus(ret)
		except urllib2.HTTPError: # Login failed
			return None
		
		matches = _rx_name_val.findall(ret);
		kuser_info = dict(map(lambda item: (item[0], item[1].decode('cp949')), matches))
		kuser_info['student_id'] = kuser_info['ku_status'].split('=')[0]
		kuser_info['department'] = kuser_info['ku_departmentname'].split('=')[1][:-1]

		try:
			user = User.objects.get(username__exact=kuser_info['uid'])
			return user
		except User.DoesNotExist:
			user = User(username=kuser_info['uid'])
			user.first_name = kuser_info['givenname']
			user.last_name = kuser_info['sn']
			user.email = kuser_info['mail']
			user.set_unusable_password()
			user.save()
			profile = UserProfile()
			profile.user = user
			profile.language = u'ko-kr'
			profile.department = Department.objects.get(name__exact=kuser_info['department'])
			profile.student_id = kuser_info['student_id']
			profile.save()
			return user
	
	def get_user(self, user_id):
		try:
			return User.objects.get(pk==user_id)
		except User.DoesNotExist:
			return None


# For Testing
if __name__ == '__main__':
	import getpass
	b = KAISTSSOBackend()
	username = raw_input('Username: ')
	password = getpass.getpass()
	b.authenticate(username, password)
