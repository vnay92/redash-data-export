
"""
Demonstrates how to use the background scheduler to schedule a job that executes on 3 second
intervals.
"""
import os
import time
import logging

from datetime import datetime
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
        all_jobs = Jobs.objects.filter(is_active=True)
        for job in all_jobs:
            Scheduler.scheduler.add_job(
                Scheduler.schedule_job,
                'interval',
                id=str(job.id),
                minutes=(job.schedule * 60),
                args=[job]
            )
            logging.info(f'Added the Job {job.id} to the scheduler with an interval of {job.schedule} minutes')

        Scheduler.scheduler.add_job(Scheduler.schedule_export_workers, 'interval', id='default', seconds=30)
        Scheduler.scheduler.add_job(
            Scheduler.schedule_export_workers,
            'interval',
            id='executed',
            seconds=30,
            args=['EXECUTED']
        )

        Scheduler.scheduler.add_job(
            Scheduler.schedule_export_workers,
            'interval',
            id='downloaded',
            seconds=30,
            args=['DOWNLOADED']
        )

        Scheduler.scheduler.add_job(
            Scheduler.schedule_export_workers,
            'interval',
            id='saved_to_storage',
            seconds=30,
            args=['SAVED_TO_STORAGE']
        )

        Scheduler.scheduler.add_job(
            Scheduler.schedule_export_workers,
            'interval',
            id='mailed',
            seconds=30,
            args=['MAILED']
        )

        logging.info(
            f'Added the Worker scheduler with an interval of 30 seconds'
        )
        Scheduler.scheduler.start()

    @staticmethod
    def schedule_job(job):
        call_command('schedule_export', job_id=job.id)

    @staticmethod
    def schedule_export_workers(status='PENDING'):
        call_command('check_export_status', status=status)

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
            minutes=(job.schedule * 60),
            args=[job]
        )
