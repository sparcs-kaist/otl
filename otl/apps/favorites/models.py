from django.db import models
from django.contrib.auth.models import User

class CourseLink(models.Model):
	lec_code = models.CharField(max_length=10)
	year = models.IntegerField()
	semester = models.CharField(max_length=1)
	url = models.URLField(max_length=200)
	cnt = models.IntegerField()
	writer_id = models.IntegerField()
	wirte_time = models.DateTimeField()
	favorite_list = models.ManyToManyField(User, through = 'FavoriteList')

class FavoriteList(models.Model):
	user = models.ForeignKey(User)
	link = models.ForeignKey(CourseLink)
	

