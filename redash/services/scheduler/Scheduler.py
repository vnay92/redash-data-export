import os
import logging

from django.utils import timezone
from redash.models.jobs import Jobs
from django.core.management import call_command

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

# Get an instance of a logger
logging.basicConfig()
logging.getLogger('redash').setLevel(logging.INFO)


class Scheduler:
    url = f"mysql://{os.getenv('DATABASE_USERNAME')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
    scheduler = BackgroundScheduler({
        'apscheduler.jobstores.mysql': {
            'type': 'sqlalchemy',
            'url': url
        },
    })

    @staticmethod
    def start_schedulers():
        all_jobs = Jobs.objects.filter(
            is_active=True, is_scheduled=False, schedule_start_time__lt=timezone.now(), schedule_end_time__gt=timezone.now())

        existing_job = None
        for job in all_jobs:
            existing_job = Scheduler.scheduler.get_job(job_id=job.id)
            if existing_job:
                continue

            Scheduler.add_job(job=job)
            logging.info(
                f'Added the Job {job.id} to the scheduler with an interval of {job.schedule} minutes')

        statuses_to_retry = [
            'MAILED',
            'PENDING',
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
                args=[status_to_retry],
                jobstore='default'
            )

            logging.info(
                f'Added the Worker scheduler with an interval of 30 seconds for the status: {status_to_retry}'
            )

        Scheduler.scheduler.add_job(
            Scheduler.add_delayed_jobs,
            'interval',
            id='delayed_schedules',
            seconds=30,
            jobstore='default'
        )

        Scheduler.scheduler.add_job(
            Scheduler.remove_stale_jobs,
            'interval',
            id='remove_schedules',
            seconds=30,
            jobstore='default'
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
    def remove_job(id, job_store='mysql'):
        Scheduler.scheduler.remove_job(str(id), jobstore=job_store)

    @staticmethod
    def add_job(job=None, id=None, job_store='mysql'):
        logger = logging.getLogger(__name__)
        if job == None:
            job = Jobs.objects.get(id=id)

        if not job.is_active:
            return

        if isinstance(job.schedule, str):
            job.schedule = int(float(job.schedule))

        now = timezone.now().time()
        job_time = job.schedule_start_time.time()
        diff = abs(now.hour - job_time.hour)
        should_skip_job = diff % job.schedule

        logger.info(f'[SCHEDULER] Values for Checking the should Skip Job')
        logger.info({
            'now': now,
            'diff': diff,
            'job_time': job_time,
            'should_skip_job': should_skip_job,
        })

        logger.info(
            f'[SCHEDULER] Should Skip for the job id: {job.id}, {should_skip_job}')

        if should_skip_job:
            return

        # Making sure the first instance is run.
        if job.schedule == 24:
            call_command('schedule_export', job_id=job.id)

        Scheduler.scheduler.add_job(
            Scheduler.schedule_job,
            'interval',
            id=str(job.id),
            seconds=(job.schedule * 60 * 60),
            name=(job.query_name + '-' + str(job.id)),
            args=[job],
            jobstore=job_store
        )
