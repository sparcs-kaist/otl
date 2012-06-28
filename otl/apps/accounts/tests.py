# -*- coding: utf-8
from django.conf import settings
from django.utils import simplejson as json
from django.test import TestCase
from django.core.exceptions import *
from otl.apps.timetable.models import Lecture, Timetable
from django.contrib.auth.models import User
from otl.apps.accounts.models import UserProfile, Department
import sys
from otl.apps.tests import *

class AccountsTestCase(BaseTestCase):
    def testLogin(self):
        response = self.client.post('/login/?next=/', {'username':'test_user1', 'password':'123'})
        #result = json.loads(response.content)

        self.assertEqual(response.status_code, 302, 'Status check')

    def testLogout(self):
        response = self.client.post('/logout/')
        self.assertEqual(response.status_code, 302, 'Status check')

    def testLoginFail(self):
        response = self.client.post('/login/?next=/', {'username':'test_user1', 'password':'1234'})
        self.assertNotEqual(response.status_code, 302, 'Status check')
        response = self.client.post('/login/?next=/', {'username':'test_user3', 'password':'124'})
        self.assertNotEqual(response.status_code, 302, 'Status check')

    def testMyInfo(self):
        self.client.login(username='test_user2', password='123')
        response = self.client.post('/accounts/myinfo/', {'favorite_departments':['532', '110', '151'], 'language':['ko-KR']})
        self.assertEqual(response.status_code, 302, 'Status check')
        user = User.objects.get(username='test_user2')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(set([item.id for item in profile.favorite_departments.all()]), set([532, 110, 151]))

