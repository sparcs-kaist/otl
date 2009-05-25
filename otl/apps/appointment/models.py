# encoding: utf-8
from django.db import models
from datetime import datetime

"""
약속잡기의 동작 과정
--------------------

1. 약속 제안자(Appointment.owner)가 약속 item을 만든다.
   이때 어떤 시간대에 약속을 잡았으면 좋겠다는 의미의 후보 시간(CandidateTimeRange)을 표시한다.
   약속 제안자는 참여를 원하는 다른 사용자들에게 이 약속 item의 permalink(Appointment.hash)를 알려준다.

2. 참여자들은 그 permalink를 통해 약속 item에 접근한다. 이때 참여 여부를 확인한다. (Participating 관계 생성)
   후보 시간, 자신의 일정, 다른 사람의 일정을 참고하여 자신이 원하는 시간(ParticipatingTimeRange)을 정하고 확정을 누른다(Participating.confirmed=True).

3. 모든 사람의 확정이 완료되면, 약속 제안자는 최종 약속 시간을 결정할 수 있다.
   하나의 시간대를 잡아 결정하면(Appointment.completed=True) 해당 시간은 각 사용자의 Schedule로 만들어진다.
   이때 Calendar는 기본 제공되는 약속 Calendar(system_id='appointment')를 사용한다.
   이후부터는 해당 약속 item에는 새로운 참여자가 접근할 수 없다. (Appointment.participants에 속한 사람만 접근 가능)

4. cron job을 통해 생성 시간(Appointment.created)가 1개월 이상 지난 item은 주기적으로 삭제한다.

NOTE: CandidateTimeRange는 Appointment 하나 당 여러 개를 추가할 수 있고(예: 월수금 저녁 7-9시 => 3개),
      마찬가지로 ParticipatingTimeRange는 Participating 관계 하나 당 여러 개를 설정할 수 있다.
"""

class Appointment(models.Model):
	hash = models.CharField(max_length=32)
	owner = models.ForeignKey('auth.User')
	group = models.ForeignKey('groups.GroupBoard', blank=True, null=True)
	participants = models.ManyToManyField('auth.User', related_name='participating_appointments', through='Participating')
	created = models.DateTimeField(default=datetime.now)
	summary = models.CharField(max_length=120)
	completed = models.BooleanField(default=False)

	# Finally decided appointment time
	date = models.DateField(blank=True)
	time_start = models.TimeField(blank=True)
	time_end = models.TimeField(blank=True)

class Participating(models.Model):
	participant = models.ForeignKey('auth.User')
	appointment = models.ForeignKey(Appointment)
	confirmed = models.BooleanField(default=False)

class CandidateTimeRange(models.Model):
	belongs_to = models.ForeignKey(Appointment, related_name='candidate_times')
	date = models.DateField()
	time_start = models.TimeField()
	time_end = models.TimeField()

class ParticipatingTimeRange(models.Model):
	belongs_to = models.ForeignKey(Participating, related_name='participating_times')
	date = models.DateField()
	time_start = models.TimeField()
	time_end = models.TimeField()
