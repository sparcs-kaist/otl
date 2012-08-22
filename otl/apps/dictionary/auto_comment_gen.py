# -*- coding: utf-8
from django.contrib.auth.models import User
from otl.apps.accounts.models import UserProfile, Department
from otl.apps.timetable.models import Lecture
from otl.apps.dictionary.models import Course, Comment

#writer =  User.objects.get(username='test_user')

lecture = Lecture.objects.filter(code='36.330')[0]
course = Course.objects.get(old_code='CS330')
dep = Department.objects.get(id=532)

users = User.objects.all()
profiles = UserProfile.objects.all()
comments = Comment.objects.all()
profiles.delete()
users.delete()
comments.delete()

for n in range(1,100):
    writer_name = "kid%d"%n
    writer = User(username=writer_name)
    writer.set_password("1234")
    writer.save()
    sid=20120010
    writer_profile = UserProfile(user=writer, student_id=str(sid+n), department=dep, nickname=writer_name, language="ko")
    writer_profile.save()
    writer_profile.take_lecture_list.add(lecture)
    writer_profile.save()
    comment_text = "코멘트%d by %s"%(n,writer_name)
    comment = Comment(course=course, lecture=lecture, writer=writer, comment=comment_text, load=1, score=1, gain=1)
    comment.save()


