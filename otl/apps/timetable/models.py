# encoding: utf-8
from django.db import models
from otl.apps.accounts.models import Department

CLASS_TYPES = (
	('l', u'강의'),
	('e', u'실험'),
)

class Lecture(models.Model):
	"""특정 년도·학기에 개설된 과목 instance를 가리키는 모델"""
	code = models.CharField(max_length=10)					# 과목코드
	year = models.IntegerField()							# 개설년도 (4자리 숫자)
	semester = models.SmallIntegerField()		   			# 개설학기 (1=봄, 2=여름, 3=가을, 4=겨울)
	department = models.ForeignKey(Department)	   			# 학과
	class_no = models.CharField(max_length=4)				# 분반
	title = models.CharField(max_length=100)	   			# 과목이름 (한글)
	title_en = models.CharField(max_length=100)	   			# 과목이름 (영문)
	type = models.CharField(max_length=12)		   			# 과목구분 (한글; '전필', '전선', '기필', ...)
	type_en = models.CharField(max_length=36)	   			# 과목구분 (영문; 'Major Required', 'Major Elective', ...)
	credit = models.IntegerField()				   			# 학점
	credit_au = models.IntegerField()			   			# AU
	class_time = models.CharField(max_length=100, null=True)	# 수업시간 (문자열로 설명만 되어 있는 것)
	lab = models.CharField(max_length=100, null=True)		# 실험시간 (상동)
	limit = models.IntegerField(default=0)		   			# 인원제한
	professor = models.CharField(max_length=100)   			# 교수님 이름 (한글)
	professor_en = models.CharField(max_length=100)			# 교수님 이름 (영문)
	notice = models.CharField(max_length=200, null=True)	# 비고
	is_english = models.BooleanField()						# 영어강의 여부

	class Meta:
		unique_together = ('code', 'year', 'semester', 'department', 'class_no')

class ExamTime(models.Model):
	"""Lecture에 배정된 시험 시간."""
	lecture = models.ForeignKey(Lecture)
	day = models.SmallIntegerField()				# 시험 요일 (1~5: 월~금)
	begin = models.CharField(max_length=5)			# hh:mm 형태의 시험 시작 시간 (24시간제)
	end = models.CharField(max_length=5)			# hh:mm 형태의 시험 종료 시간 (24시간제)

class ClassTime(models.Model):
	"""Lecture에 배정된 강의 시간. 보통 하나의 Lecture가 여러 개의 강의 시간을 가진다."""
	lecture = models.ForeignKey(Lecture)			
	day = models.SmallIntegerField()
	begin = models.CharField(max_length=5)
	end = models.CharField(max_length=5)
	type = models.CharField(max_length=1, choices=CLASS_TYPES)
	building = models.CharField(max_length=10)	# 건물 고유ID (잘 사용되지 않음)
	room = models.CharField(max_length=60)		# 호실 (잘 사용되지 않음)
	room_ko = models.CharField(max_length=60)	# 수업 장소 (한글)
	room_en = models.CharField(max_length=60)	# 수업 장소 (영문)
	unit_time = models.SmallIntegerField()		# 수업 교시

class Syllabus(models.Model):
	"""Lecture에 대한 강의계획서 정보. 첨부파일로만 나오고 비어있는 경우도 있음."""
	lecture = models.ForeignKey(Lecture)
	professor_info = models.CharField(max_length=60)			# 교수님 정보
	abstract = models.TextField(null=True)						# 요약 정보
	evaluation = models.TextField(null=True)					# 평가 방법
	plan = models.TextField(null=True)							# 강의 계획
	materials = models.TextField(null=True)						# 교재
	etc = models.TextField(null=True)							# 기타
	url = models.URLField(null=True)							# 과목 홈페이지
	attachment = models.CharField(max_length=260, null=True)	# 첨부파일 이름

# TODO: 수강신청 현황 View에 대응하는 Table

# vim: set ts=4 sts=4 sw=4 noet:
