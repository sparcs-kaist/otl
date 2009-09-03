# -*- coding: utf-8
from django.contrib import auth
from django.contrib.auth.models import User
from otl.apps.accounts.models import UserProfile, Department, get_dept_from_deptname
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
            ('b003', 'ku_regno1'),
            #('b003', 'ku_regno2'), # We don't need the civil registration number.
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
        if ';:' in kuser_info['ku_departmentname']: # users merged from ICU
            kuser_info['department'] = kuser_info['ku_departmentname'].split('=')[1].split(';')[0]
        else: # original KAIST users
            kuser_info['department'] = kuser_info['ku_departmentname'].split('=')[1][:-1]

        try:
            user = User.objects.get(username__exact=kuser_info['uid'])
            user.first_login = False

            # If this user already exists in our database, just pass or update his info.
            profile = UserProfile.objects.get(user=user)
            changed = False
            new_dept = get_dept_from_deptname(kuser_info['department'])
            if profile.department.name != new_dept.name:
                profile.department = new_dept
                changed = True
            if profile.student_id != kuser_info['student_id']:
                profile.student_id = kuser_info['student_id']
                changed = True

            if changed:
                profile.save()
            return user

        except UserProfile.DoesNotExist:

            # This may occur when a user stopped at the privacy agreement step and retry afterwards.
            user.kuser_info = kuser_info
            user.first_login = True
            return user

        except User.DoesNotExist:

            # If this user doesn't exist yet, make records for him.
            user = User(username=kuser_info['uid'])
            user.first_name = kuser_info['givenname']
            user.last_name = kuser_info['sn']
            user.email = kuser_info['mail']
            user.set_unusable_password() # We don't save the password.
            user.save()

            # These two fields are for passing privacy info temporarily.
            user.kuser_info = kuser_info
            user.first_login = True
            return user
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# For Testing
if __name__ == '__main__':
    import getpass
    b = KAISTSSOBackend()
    username = raw_input('Username: ')
    password = getpass.getpass()
    b.authenticate(username, password)
