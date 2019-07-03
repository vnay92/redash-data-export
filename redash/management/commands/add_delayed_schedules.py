import logging

from io import StringIO
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand

from redash.models.jobs import Jobs
from redash.services.scheduler import Scheduler
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
            is_active=True) #, schedule_start_time__lte=timezone.now(), schedule_end_time__gte=timezone.now())

        now = timezone.now().time()
        for job in jobs:
            self.logger.info(f'Time of the Cron {job.schedule_start_time.time()}')
            if now.hour != job.schedule_start_time.time().hour or now.minute != job.schedule_start_time.time().minute:
                continue

            try:
                Scheduler.add_job(job)
                self.logger.info(f'Added the job to schedule {job}')
            except Exception as e:
                self.logger.error(
                    f'Error in Adding the Job.. {e}')
