# -*- coding: utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import *
from otl.apps.accounts.models import UserProfile
from optparse import make_option
from datetime import time
import sys, getpass, re
import Sybase

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = u'Initialize recent score of users'

    def handle(self, *args, **options):
        for user in UserProfile.objects.all():
            user.recent_score = 0
            user.save()

        print 'Recent score initialization completed.'

