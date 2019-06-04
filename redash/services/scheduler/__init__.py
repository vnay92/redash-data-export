
import os
import time
import logging

from datetime import datetime
from django.utils import timezone
from redash.models.jobs import Jobs
from django.core.management import call_command
from apscheduler.schedulers.background import BackgroundScheduler

# Get an instance of a logger
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)


class Scheduler:
    scheduler = BackgroundScheduler()

    @staticmethod
    def start_schedulers():
        all_jobs = Jobs.objects.filter(
            is_active=True)
        for job in all_jobs:
            Scheduler.add_job(job=job)
            logging.info(
                f'Added the Job {job.id} to the scheduler with an interval of {job.schedule} minutes')

        statuses_to_retry = [
            'PENDING',
            'MAILED',
            'EXECUTED',
            'DOWNLOADED',
            'SAVED_TO_STORAGE',
        ]

        for status_to_retry in statuses_to_retry:
            Scheduler.scheduler.add_job(
                Scheduler.schedule_export_workers,
                'interval',
                id=status_to_retry.lower(),
                seconds=30,
                args=[status_to_retry]
            )

            logging.info(
                f'Added the Worker scheduler with an interval of 30 seconds for the status: {status_to_retry}'
            )

        Scheduler.scheduler.add_job(
            Scheduler.add_delayed_jobs,
            'interval',
            id='remove_schedules',
            seconds=60
        )

        Scheduler.scheduler.add_job(
            Scheduler.remove_stale_jobs,
            'interval',
            id='delayed_schedules',
            seconds=60
        )

        Scheduler.scheduler.start()

    @staticmethod
    def schedule_job(job):
        call_command('schedule_export', job_id=job.id)

    @staticmethod
    def schedule_export_workers(status='PENDING'):
        call_command('check_export_status', status=status)

    @staticmethod
    def add_delayed_jobs():
        call_command('add_delayed_schedules')

    @staticmethod
    def remove_stale_jobs():
        call_command('remove_stale_schedules')

    @staticmethod
    def remove_job(id):
        Scheduler.scheduler.remove_job(str(id))

    @staticmethod
    def add_job(job=None, id=None):
        if job == None:
            job = Jobs.objects.get(id=id)

        if not job.is_active:
            return

        Scheduler.scheduler.add_job(
            Scheduler.schedule_job,
            'interval',
            id=str(job.id),
            seconds=(job.schedule * 60 * 60),
            args=[job]
        )
