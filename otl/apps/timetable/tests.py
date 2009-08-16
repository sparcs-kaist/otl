# -*- coding: utf-8
from django.conf import settings
from django.utils import simplejson as json
from django.test import TestCase
from django.core.exceptions import *
from otl.apps.timetable.models import Lecture, Timetable
import sys

class TimetableTestCase(TestCase):

    fixtures = ['apps/accounts/fixtures/test.json', 'apps/timetable/fixtures/test.json']

    def setUp(self):
        settings.NEXT_YEAR = 2009
        settings.NEXT_SEMESTER = 1
        self.client.login(username='test_user', password='whkwjfrmawl')

    def testAddToTimetable(self):
        # Try to add the test data
        response = self.client.get('/timetable/add/', {'table_id': 1, 'lecture_id': 2})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertTrue(Timetable.objects.get(lecture__pk = 2, table_id = 1) != None, 'DB consistency check')

    def testDeleteFromTimetable(self):
        # Add a test data
        response = self.client.get('/timetable/add/', {'table_id': 2, 'lecture_id': 1})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertTrue(Timetable.objects.get(lecture__pk = 1, table_id = 2) != None, 'DB consistency check')

        # Try to delete a wrong data
        response = self.client.get('/timetable/delete/', {'table_id': 999, 'lecture_id': 1})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'NOT_EXIST', 'Result message check')
        self.assertTrue(Timetable.objects.get(lecture__pk = 1) != None, 'DB consistency check')

        # Try to delete the test data
        response = self.client.get('/timetable/delete/', {'table_id': 2, 'lecture_id': 1})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertRaises(ObjectDoesNotExist, lambda: Timetable.objects.get(lecture__pk = 1, table_id = 2))

    def testAddToTimetableOverlapped(self):
        # Try to add the test data
        response = self.client.get('/timetable/add/', {'table_id': 3, 'lecture_id': 3})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertTrue(Timetable.objects.get(lecture__pk = 3, table_id = 3) != None, 'DB consistency check')

        # Try to add the overlapping data
        response = self.client.get('/timetable/add/', {'table_id': 3, 'lecture_id': 1})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OVERLAPPED', 'Result message check')
        self.assertRaises(ObjectDoesNotExist, lambda: Timetable.objects.get(lecture__pk = 1, table_id = 3))
    
    def testViewTimetable(self):
        # Try to add the test data
        Timetable.objects.all().delete()
        response = self.client.get('/timetable/add/', {'table_id': 1, 'lecture_id': 3})
        result = json.loads(response.content)
        self.assertEqual(result['result'], 'OK', 'Result message check')
        response = self.client.get('/timetable/add/', {'table_id': 3, 'lecture_id': 4})
        result = json.loads(response.content)
        self.assertEqual(result['result'], 'OK', 'Result message check')
        response = self.client.get('/timetable/add/', {'table_id': 2, 'lecture_id': 2})
        result = json.loads(response.content)
        self.assertEqual(result['result'], 'OK', 'Result message check')
        response = self.client.get('/timetable/add/', {'table_id': 1, 'lecture_id': 1})
        result = json.loads(response.content)
        self.assertEqual(result['result'], 'OVERLAPPED', 'Result message check')
        response = self.client.get('/timetable/add/', {'table_id': 3, 'lecture_id': 2})
        result = json.loads(response.content)
        self.assertEqual(result['result'], 'OK', 'Result message check')
        response = self.client.get('/timetable/add/', {'table_id': 2, 'lecture_id': 1})
        result = json.loads(response.content)
        self.assertEqual(result['result'], 'OK', 'Result message check')
        response = self.client.get('/timetable/add/', {'table_id': 3, 'lecture_id': 3})
        result = json.loads(response.content)
        self.assertEqual(result['result'], 'OK', 'Result message check')

        response = self.client.get('/timetable/view/', {'table_id': 1})
        result = json.loads(response.content)
        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertEqual(len(result['data']), 1, 'Length of result data')
        self.assertEqual(Timetable.objects.filter(table_id = 1).count(), 1, 'DB consistency check')

        response = self.client.get('/timetable/view/', {'table_id': 2})
        result = json.loads(response.content)
        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertEqual(len(result['data']), 2, 'Length of result data')
        self.assertEqual(Timetable.objects.filter(table_id = 2).count(), 2, 'DB consistency check')

        response = self.client.get('/timetable/view/', {'table_id': 3})
        result = json.loads(response.content)
        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertEqual(len(result['data']), 3, 'Length of result data')
        self.assertEqual(Timetable.objects.filter(table_id = 3).count(), 3, 'DB consistency check')

