# -*- coding: utf-8
from django.conf import settings
from django.utils import simplejson as json
from django.test import TestCase
from django.core.exceptions import *
from otl.apps.timetable.models import Lecture, Department, ClassTime
from otl.apps.dictionary.models import Course, Professor
from otl.apps.tests import *
from datetime import *
import sys

class TimetableTestCase(BaseTestCase):
    #fixtures = ['apps/accounts/fixtures/test.json', 'apps/timetable/fixtures/test.json']
    def setUp(self):
        BaseTestCase.setUp(self)
        settings.NEXT_YEAR = 2009
        settings.NEXT_SEMESTER = 1
        dep = Department.objects.get(id=532)
        course = Course(old_code='CS330', department=dep, type='전필', type_en='Major Required', title='운영체제 및 실험', score_average=0, load_average=0, gain_average=0)
        course.save()

        ''' Create Lecture 1 '''
        lecture1 = Lecture(code='36.330', old_code='CS330', class_no ='A', title='운영체제 및 실험', type='전필', type_en='Major Required', audience=0, credit=4, semester=3,year=2009, is_english=True, department=dep, course=course)
        lecture1.save()

        time1 = ClassTime(lecture=lecture1, day=0, begin=time(13,0), end=time(16,0))
        time1.save()

        prof = Professor(professor_name='테스트교수', professor_id=100)
        prof.save()
        lecture1.professor.add(prof)

        ''' Create Lecture 2 '''
        lecture2 = Lecture(code='36.330', old_code='CS330', class_no ='B', title='운영체제 및 실험', type='전필', type_en='Major Required', audience=0, credit=4, semester=3,year=2009, is_english=True, department=dep, course=course)
        lecture2.save()

        time2 = ClassTime(lecture=lecture2, day=0, begin=time(15,0), end=time(17,0))
        time2.save()

        ''' Create Lecture 3 '''
        lecture3 = Lecture(code='36.330', old_code='CS330', class_no ='A', title='운영체제 및 실험', type='전필', type_en='Major Required', audience=0, credit=4, semester=1,year=2010, is_english=True, department=dep, course=course)
        lecture3.save()

        time3 = ClassTime(lecture=lecture3, day=0, begin=time(15,0), end=time(17,0))
        time3.save()
        self.client.login(username='test_user1', password='123')

        ''' Create Lecture 4 '''
        lecture4 = Lecture(code='36.330', old_code='CS330', class_no ='C', title='운영체제 및 실험', type='전필', type_en='Major Required', audience=0, credit=4, semester=3,year=2009, is_english=True, department=dep, course=course)
        lecture4.save()

        time4 = ClassTime(lecture=lecture4, day=1, begin=time(14,0), end=time(17,0))
        time4.save()

    def testAddToTimetable(self):
        # Try to add the test data
        lecture1 = Lecture.objects.get(id=1)
        response = self.client.get('/timetable/add/', {'table_id': 0, 'lecture_id': lecture1.id, 'view_year': lecture1.year, 'view_semester': lecture1.semester})
        result = json.loads(response.content)

        self.assertEqual(Lecture.objects.get(class_no='B').id,2,'id ERROR')

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertTrue(Timetable.objects.get(lecture__pk = 1, table_id = 0) != None, 'DB consistency check')

        # Try to add the same data
        response = self.client.get('/timetable/add/', {'table_id': 0, 'lecture_id': lecture1.id, 'view_year': lecture1.year, 'view_semester': lecture1.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OVERLAPPED', 'Result message check')

        # Try to add the other overlapped data
        lecture2 = Lecture.objects.get(id=2)
        response = self.client.get('/timetable/add/', {'table_id': 0, 'lecture_id': lecture2.id, 'view_year': lecture2.year, 'view_semester': lecture2.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OVERLAPPED', 'Result message check')

    def testDeleteFromTimetable(self):
        # Add a test data
        lecture = Lecture.objects.get(id=1)
        response = self.client.get('/timetable/add/', {'table_id': 2, 'lecture_id': lecture.id, 'view_year': lecture.year, 'view_semester': lecture.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertTrue(Timetable.objects.get(lecture__pk = 1, table_id = 2) != None, 'DB consistency check')

        # Try to delete a wrong data
        response = self.client.get('/timetable/delete/', {'table_id': 1, 'lecture_id': lecture.id, 'view_year': lecture.year, 'view_semester': lecture.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'NOT_EXIST', 'Result message check')
        self.assertTrue(Timetable.objects.get(lecture__pk = 1, table_id = 2) != None, 'DB consistency check')

        # Try to delete the test data
        response = self.client.get('/timetable/delete/', {'table_id': 2, 'lecture_id': 1})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertRaises(ObjectDoesNotExist, lambda: Timetable.objects.get(lecture__pk = 1, table_id = 2))

    def testChangeSemester(self):
        # Setting lectures
        lecture1 = Lecture.objects.get(id=1)
        lecture2 = Lecture.objects.get(id=4)
        lecture3 = Lecture.objects.get(id=3)
        # Add a test data
        response = self.client.get('/timetable/add/', {'table_id': 0, 'lecture_id': lecture1.id, 'view_year': lecture1.year, 'view_semester': lecture1.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')

        response = self.client.get('/timetable/add/', {'table_id': 0, 'lecture_id': lecture2.id, 'view_year': lecture2.year, 'view_semester': lecture2.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')

        response = self.client.get('/timetable/add/', {'table_id': 1, 'lecture_id': lecture2.id, 'view_year': lecture2.year, 'view_semester': lecture2.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')

        response = self.client.get('/timetable/add/', {'table_id': 1, 'lecture_id': lecture3.id, 'view_year': lecture3.year, 'view_semester': lecture3.semester})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')

        # Change to 2009 fall semester
        response = self.client.get('/timetable/change/', {'view_year': 2009, 'view_semester': 3})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertEqual(len(result['data'][0]), 2, 'Data check')
        self.assertEqual(len(result['data'][1]), 1, 'Data check')
        self.assertEqual(len(result['data'][2]), 0, 'Data check')

        # Change to 2010 spring semester
        response = self.client.get('/timetable/change/', {'view_year': 2010, 'view_semester': 1})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(result['result'], 'OK', 'Result message check')
        self.assertEqual(len(result['data'][0]), 0, 'Data check')
        self.assertEqual(len(result['data'][1]), 1, 'Data check')
        self.assertEqual(len(result['data'][2]), 0, 'Data check')

    def testSearch(self):
        # Search for time
        response = self.client.get('/timetable/search/', {'year': 2009, 'term': 3, 'start_day': 0, 'end_day': 0, 'start_time': 480, 'end_time': 1320, 'type':u'전체보기'})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(len(result), 2, 'Searched data check')

        # Search for department
        response = self.client.get('/timetable/search/', {'year': 2009, 'term': 3, 'dept': 532, 'type': u'전체보기', 'keyword':''})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(len(result), 3, 'Searched data check')

        # Search for keyword
        response = self.client.get('/timetable/search/', {'year': 2010, 'term': 1, 'dept': -1, 'type': u'전체보기', 'keyword': u'운영체제'})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(len(result), 1, 'Searched data check')

        # Search for professor
        response = self.client.get('/timetable/search/', {'year': 2009, 'term': 3, 'dept': -1, 'type': u'전체보기', 'keyword': u'테스트교수'})
        result = json.loads(response.content)

        self.assertEqual(response.status_code, 200, 'Status check')
        self.assertEqual(len(result), 1, 'Searched data check')

    def testTestAsPDF(self):
        response = self.client.get('/timetable/print/', {'id':0, 'view_year': 2009, 'view_semester': 3})
