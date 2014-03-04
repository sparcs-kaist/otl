OTL
=====

이 저장소는 OTL(Online Timeplanner with Lectures)의 서비스에 사용되는 소스의 저장소입니다.
OTL은 django, javascript의 frontend와 python backend로 구성되어 있습니다.

문의는

	otlproject at 5parc5.org (replace 5 to s)

로 메일을 보내주세요.

개발 환경 세팅하기
-----

	$ cd otl
	$ python manage.py syncdb
	$ python manage.py loaddata test
	$ python manage.py runserver

Dependencies
-----

* Django >= 1.2
* MySQL-python
* PIL (Python Imaging Library)
* django-extensions

Links
-----

<dl>
  <dt>OTL (Production)</dt>
  <dd>http://otl.kaist.ac.kr/</dd>
  <dt>SPARCS, developers' group in KAIST (Korea Advanced Institute of Science and Technology)</dt>
  <dd>http://sparcs.org</dd>
</dl>
     
