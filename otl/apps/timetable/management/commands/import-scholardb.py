# -*- coding: utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import *
from otl.apps.accounts.models import Department
from otl.apps.timetable.models import Lecture, ClassTime, ExamTime
from optparse import make_option
from datetime import time
import sys, getpass, re
import Sybase

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--host', dest='host', help=u'Specifies server address.'),
        make_option('--user', dest='user', help=u'Specifies user name to log in.'),
        make_option('--password', dest='password', help=u'Specifies passowrd to log in.'),
        make_option('--encoding', dest='encoding', help=u'Sepcifies character encoding to decode strings from database. (default is cp949)', default='cp949'),
        make_option('--exclude-lecture', action='store_true', dest='exclude_lecture', help=u'Don\'t update lecture information when you want to update time information only.', default=False),
    )
    help = u'Imports KAIST scholar database.'
    args = u'--host=143.248.X.Y:PORT --user=USERNAME'

    def handle(self, *args, **options):
        rx_dept_code = re.compile(ur'([a-zA-Z]+)(\d+)')
        host = options.get('host', None)
        user = options.get('user', None)
        password = options.get('password', None)
        encoding = options.get('encoding', 'cp949')
        exclude_lecture = options.get('exclude_lecture', False)
        lecture_count = 0
        try:
            if password is None:
                password = getpass.getpass()
        except (KeyboardInterrupt, EOFError):
            print
            return

        try:
            db = Sybase.connect(host, user, password, 'scholar')
        except Sybase.DatabaseError:
            print>>sys.stderr, u'Connection failed. Check username and password.'
            return
        c = db.cursor()

        if not exclude_lecture:
            c.execute('SELECT * FROM view_OTL_lecture WHERE lecture_year = %d AND lecture_term = %d ORDER BY dept_id' % (settings.NEXT_YEAR, settings.NEXT_SEMESTER))
            rows = c.fetchall()
            departments = {}
            lectures_not_updated = set()

            for lecture in Lecture.objects.filter(year = settings.NEXT_YEAR, semester = settings.NEXT_SEMESTER):
                lectures_not_updated.add((
                    lecture.code,
                    lecture.year,
                    lecture.semester,
                    lecture.department.id,
                    lecture.class_no,
                ))

            prev_department = None
            for row in rows:
                myrow = []
                for elem in row:
                    if isinstance(elem, str):
                        elem = elem.decode(encoding)
                    myrow.append(elem)

                # Extract department info.
                lecture_no = myrow[2]
                lecture_code = myrow[20]
                lecture_class_no = myrow[3].strip()
                department_no = int(lecture_no[0:2])
                department_id = int(myrow[4])
                department_code = rx_dept_code.match(lecture_code).group(1)

                # Update department info.
                if prev_department != department_id:
                    try:
                        department = Department.objects.get(id = department_id)
                        print u'Updating department: %s' % department
                    except Department.DoesNotExist:
                        department = Department(id = department_id)
                        print u'Adding department: %s(%d)...' % (department_code, department_id)
                    department.num_id = department_no
                    department.code = department_code
                    department.name = myrow[5]
                    department.name_en = myrow[6]
                    department.save()

                prev_department = department_id

                # Extract lecture info.
                print u'Retreiving %s: %s [%s]...' % (lecture_code, myrow[7], lecture_class_no)
                lecture_key = {
                    'code': lecture_no,
                    'year': int(myrow[0]),
                    'semester': int(myrow[1]),
                    'department': Department.objects.get(id = department_id),
                    'class_no': lecture_class_no,
                }
                # Convert the key to a hashable object (tuple).
                lecture_key_hashable = (
                    lecture_no,
                    int(myrow[0]),
                    int(myrow[1]),
                    department_id,
                    lecture_class_no,
                )
                try:
                    lecture = Lecture.objects.get(**lecture_key)
                    print u'Updating existing lecture...'
                except Lecture.DoesNotExist:
                    lecture = Lecture(**lecture_key)
                    print u'Creating new lecture...'

                # Update lecture info.
                lecture.old_code = myrow[20]
                lecture.title = myrow[7]
                lecture.title_en = myrow[8]
                lecture.type = myrow[10]        # 과목구분 (한글)
                lecture.type_en = myrow[11]     # 과목구분 (영문)
                lecture.professor = myrow[18]       # 교수님 이름 (한글)
                lecture.professor_en = myrow[22]    # 교수님 이름 (영문)
                lecture.audience = int(myrow[12])   # 학년 구분
                lecture.limit= myrow[17]            # 인원제한
                lecture.credit = myrow[16]          # 학점
                lecture.credit_au = myrow[13]       # AU
                lecture.num_classes = int(myrow[14])    # 강의시수
                lecture.num_labs = int(myrow[15])       # 실험시수
                lecture.notice = myrow[19]          # 비고
                lecture.is_english = True if myrow[21] == 'Y' else False # 영어강의 여부
                lecture.deleted = False
                lecture.save()
                lecture_count += 1

                try:
                    lectures_not_updated.remove(lecture_key_hashable)
                except KeyError:
                    pass

            c.close()
        
        # Extract exam-time, class-time info.
        print u'Extracting exam time information...'
        c = db.cursor()
        c.execute('SELECT * FROM view_OTL_exam_time WHERE lecture_year = %d AND lecture_term = %d' % (settings.NEXT_YEAR, settings.NEXT_SEMESTER))
        exam_times = c.fetchall()
        c.close()
        ExamTime.objects.filter(lecture__year__exact=settings.NEXT_YEAR, lecture__semester=settings.NEXT_SEMESTER).delete()
        for row in exam_times:
            myrow = []
            for elem in row:
                if isinstance(elem, str):
                    elem = elem.decode(encoding)
                myrow.append(elem)
            lecture_key = {
                'code': myrow[2],
                'year': int(myrow[0]),
                'semester': int(myrow[1]),
                'department': Department.objects.filter(id = int(myrow[4]))[0],
                'class_no': myrow[3].strip(),
            }
            try:
                lecture = Lecture.objects.get(**lecture_key)
                exam_time = ExamTime(lecture=lecture)
                exam_time.day = int(myrow[5]) - 1
                exam_time.begin = time(hour=myrow[6].hour, minute=myrow[6].minute)
                exam_time.end = time(hour=myrow[7].hour, minute=myrow[7].minute)
                print u'Updating exam time for %s' % lecture
                exam_time.save()
            except Lecture.DoesNotExist:
                print u'Exam-time for non-existing lecture %s; skip it...' % myrow[2]

        print u'Extracting class time information...'
        c = db.cursor()
        c.execute('SELECT * FROM view_OTL_time WHERE lecture_year = %d AND lecture_term = %d' % (settings.NEXT_YEAR, settings.NEXT_SEMESTER))
        class_times = c.fetchall()
        c.close()
        ClassTime.objects.filter(lecture__year__exact=settings.NEXT_YEAR, lecture__semester=settings.NEXT_SEMESTER).delete()
        for row in class_times:
            myrow = []
            for elem in row:
                if isinstance(elem, str):
                    elem = elem.decode(encoding)
                myrow.append(elem)
            lecture_key = {
                'code': myrow[2],
                'year': int(myrow[0]),
                'semester': int(myrow[1]),
                'department': Department.objects.filter(id = int(myrow[4]))[0],
                'class_no': myrow[3].strip(),
            }
            try:
                lecture = Lecture.objects.get(**lecture_key)
                class_time = ClassTime(lecture=lecture)
                class_time.day = int(myrow[5]) - 1
                class_time.begin = time(hour=myrow[6].hour, minute=myrow[6].minute)
                class_time.end = time(hour=myrow[7].hour, minute=myrow[7].minute)
                class_time.type = myrow[8]
                class_time.building = myrow[9]
                class_time.room = myrow[10]
                class_time.room_ko = myrow[12]
                class_time.room_en = myrow[11]
                try:
                    class_time.unit_time = int(myrow[13])
                except (ValueError, TypeError):
                    class_time.unit_time = 0
                print u'Updating class time for %s' % lecture
                class_time.save()
            except Lecture.DoesNotExist:
                print u'Class-time for non-existing lecture %s; skip it...' % myrow[2]

        if not exclude_lecture:
            # Mark deleted lectures to notify users.
            print u'Marking deleted lectures...'
            for key in lectures_not_updated:
                lecture_key = {
                    'code': key[0],
                    'year': key[1],
                    'semester': key[2],
                    'department': Department.objects.get(id = key[3]),
                    'class_no': key[4],
                }
                lecture = Lecture.objects.get(**lecture_key)
                lecture.deleted = True
                print u'%s is marked as deleted...' % lecture
                lecture.save()

        db.close()

        print u'\nTotal number of departments : %d' % Department.objects.count()
        print u'Total number of lectures newly added : %d' % lecture_count
