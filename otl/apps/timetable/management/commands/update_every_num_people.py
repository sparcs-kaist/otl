# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from otl.apps.timetable.models import Lecture
from optparse import make_option
import Sybase

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--year', dest='year', help=u'Specifies year.'),
        make_option('--semester', dest='semester', help=u'Specifies semester.'),
        make_option('--all', dest='all', help=u'If you want to update for all years and semesters. True/False'),
    )
    help = u'Updates every num_people.'
    args = u'--year=20XX --semester=1(or 3)'

    def handle(self, *args, **options):
        try:
            opt_all = options.get('all', 'False')

            if opt_all == 'True':
                lectures = Lecture.objects.all()
            else:
                year = int(options.get('year', None))
                semester = int(options.get('semester', None))
                lectures = Lecture.objects.filter(year=year, semester=semester)

            for lecture in lectures:
                lecture.update_num_people()
        except:
            print 'Error occured.'
            return
