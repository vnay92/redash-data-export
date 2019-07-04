import csv
import json
import zipfile
import logging
import xlsxwriter

from io import StringIO
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand

from redash.services.scheduler.Scheduler import Scheduler
from redash.models.jobs import Jobs
from redash.models.export_logs import ExportLogs


class Command(BaseCommand):
    help = 'Schedule Export'

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument('-e', '--export_id', type=int,
                            help='Job id for which the schedule has to run')

    def handle(self, *args, **kwargs):
        self.logger.info('Export Status Cron Started')
        jobs = Jobs.objects.filter(
            is_active=True, schedule_end_time__lte=timezone.now())

        for job in jobs:
            try:
                Scheduler.remove_job(job.id)
                self.logger.info(f'removed the job from schedule {job}')
            except Exception as e:
                self.logger.error(
                    f'Error in Removing the Job.. {e}')

