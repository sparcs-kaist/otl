# encoding: utf-8
# This file includes commonly used constants and definitions.

LANGUAGES = (
	('ko-KR', u'한국어 (Korean)'),
	('en-US', u'영어 (English)'),
)
CLASS_TYPES = (
	('l', u'강의'),
	('e', u'실험'),
)
SEMESTER_TYPES = (
	(1, u'봄'),
	(2, u'여름'),
	(3, u'가을'),
	(4, u'겨울'),
)
AUDIENCE_TYPES = (
	(0, u'학사'),
	(7, u'상호인정'),
	(8, u'대학원'),
)
WEEKDAYS = (
	(0, u'월'),
	(1, u'화'),
	(2, u'수'),
	(3, u'목'),
	(4, u'금'),
	(5, u'토'),
	(6, u'일'),
)
MONTHDAYS = [(i, u'%d' % i) for i in xrange(1, 32)]
SCHEDULE_REPEAT_TYPES = (
	(1, u'매주'),
	(2, u'매월'),
)
