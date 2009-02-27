# encoding: utf8
DEPARTMENT_NAMES = [
	(8, 'URP', u'URP(학부생연구참여)'),
	(10, 'HS', u'인문사회과학부'),
	(14, 'ED', u'Freshman Design'),
	(20, 'PH', u'물리학과'),
	(21, 'BS', u'생명과학과'),
	(23, 'CH', u'화학과'),
	(25, 'MAS', u'수리과학과'),
	(31, 'IE', u'산업및시스템공학과'),
	(32, 'ID', u'산업디자인학과'),
	(33, 'NQE', u'원자력및양자공학과'),
	(34, 'MS', u'신소재공학과'),
	(35, 'EE', u'전기및전자공학전공'),
	(36, 'CS', u'전산학전공'),
	(37, 'CE', u'건설및환경공학과'),
	(39, 'CBE', u'생명화학공학과'),
	(40, 'ME', u'기계공학과'),
	(41, 'BiS', u'바이오및뇌공학과'),
	(42, 'BEP', u'Business Economics 프로그램'),
	(43, 'GCT', u'문화기술대학원'),
	(45, 'AT', u'자동차기술대학원'),
	(46, 'MSE', u'의과학대학원'),
	(47, 'RE', u'로봇공학학제전공'),
	(53, 'MGT', u'테크노경영대학원'),
	(59, 'IMB', u'아이엠비에이전공'),
	(66, 'STP', u'과학기술정책대학원프로그램'),
	(67, 'OSE', u'해양시스템공학과'),
	(68, 'ISE', u'지적서비스공학과'),
	(69, 'NST', u'나노과학기술학과'),
	(70, 'BM', u'의과학학제전공'),
	(71, 'PSE', u'고분자학학제전공'),
	(73, 'TE', u'정보통신공학학제전공'),
	(79, 'SEP', u'소프트웨어전문가과정학제전공'),
	# for compatibility
	(22, 'MA', u'수학전공'), 
	(24, 'MA', u'응용수학전공'),
	# 나머지: 자동차기술대학원, 인턴십 프로그램, 타대학 학점교환, 무학과, AP 교과목 등
]

import codecs
i = 0
f = codecs.open('departments.json', 'w', 'utf-8')

f.write('[\n')
for dn in DEPARTMENT_NAMES:
	i += 1
	f.write('\t{\n')
	f.write('\t\t"pk": "%d",\n' % i)
	f.write('\t\t"model": "accounts.department",\n')
	f.write('\t\t"fields": {"num_id": "%d", "code": "%s", "name": "%s"}\n' % dn)
	f.write('\t}')
	if i < len(DEPARTMENT_NAMES):
		f.write(',')
	f.write('\n')
f.write(']\n')

f.close()
