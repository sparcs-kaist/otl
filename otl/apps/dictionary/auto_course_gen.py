# -*- coding: utf-8
from otl.apps.dictionary.models import Course, Professor
from otl.apps.accounts.models import Department

#writer =  User.objects.get(username='test_user')

courses = Course.objects.filter(title__icontains=u'과목')
courses.delete()

department=Department.objects.get(id=532)
type = u'전공필수'
type_en = 'Major Required'
score_average = 0
load_average = 0
gain_average = 0
professor = Professor.objects.get(professor_id=284)

for n in range(0,0):
    old_code = 'CS0%02d'%n
    title = u'과목%02d'%n
    title_en = 'Course%02d'%n

    course = Course(old_code=old_code, department=department, type=type, type_en=type_en, title=title, title_en=title_en, score_average=score_average, load_average=load_average, gain_average=gain_average)
    course.save()

    course.professors.add(professor)
    course.save()
