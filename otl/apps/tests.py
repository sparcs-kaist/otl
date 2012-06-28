# -*- coding: utf-8
from django.conf import settings
from django.utils import simplejson as json
from django.test import TestCase
from django.core.exceptions import *
from otl.apps.timetable.models import Lecture, Timetable
from django.contrib.auth.models import User
from otl.apps.accounts.models import UserProfile, Department
import sys

class BaseTestCase(TestCase):
    def setUp(self):
        user1 = User(username='test_user1')
        user2 = User(username='test_user2')
        user1.set_password('123')
        user2.set_password('123')
        user1.save()
        user2.save()
        dep = Department(id=532, num_id=36, code="CS", name="전산학전공")
        dep.save()
        user_profile1 = UserProfile(user=user1, student_id='20120010', department=dep, nickname='kido1', language="ko")
        user_profile2 = UserProfile(user=user2, student_id='20120011', department=dep, nickname='kido2', language="ko")
        user_profile1.save()
        user_profile2.save()
        dep = Department(id=110, num_id=20, code="PH", name="물리학과")
        dep.save()
        dep = Department(id=151, num_id=25, code="MAS", name="수리과학과")
        dep.save()

        self.client.login(username='test_user2', password='123')
        user = User.objects.get(username='test_user2')
        profile = UserProfile.objects.get(user=user)


