# -*- coding: utf-8
from django.contrib import auth
from django.contrib.auth.models import User
from django.conf import settings
from otl.apps.accounts.models import UserProfile, Department
from SOAPpy import Config, HTTPTransport, SOAPAddress, WSDL

import urllib, urllib2
import base64
import re

class myHTTPTransport(HTTPTransport):
    username = None
    password = None

    @classmethod
    def set_authentication(cls, u, p):
        cls.username = u
        cls.password = p

    def call(self, addr, data, namespace, soapaction=None, encoding=None, http_proxy=None, config=Config):
        if not isinstance(addr, SOAPAddress):
            addr = SOAPAddress(addr, config)
        if self.username != None:
            addr.user = self.username + ":" + self.password

        return HTTPTransport.call(self, addr, data, namespace, soapaction, encoding, http_proxy, config)

class KAISTSSOBackend:
    
    def authenticate(self, user_info=None):
        if user_info == None:
            return None

        kuser_info = {}
        kuser_info['student_id'] = user_info['ku_std_no']
        kuser_info['department'] = user_info['ou']
        kuser_info['department_no'] = user_info['ku_kaist_org_id']

        try:
            user = User.objects.get(username__exact=user_info['uid'])
            user.first_login = False

            # If this user already exists in our database, just pass or update his info.
            profile = UserProfile.objects.get(user=user)
            changed = False

            try:
                new_dept = Department.objects.get(id__exact=int(user_info['ku_kaist_org_id']))
            except:
                new_dept = Department.objects.get(id__exact=0) #무학과

            if profile.department.name != new_dept.name:
                profile.department = new_dept
                changed = True
            if profile.student_id != user_info['ku_std_no']:
                profile.student_id = user_info['ku_std_no']
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
            user = User(username=user_info['uid'])
            user.first_name = user_info['givenname']
            user.last_name = user_info['sn']
            if user_info.get('mail') != None:
                user.email = user_info['mail']
            else:
                user.email = user_info['uid'] + "@kaist.ac.kr"
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
