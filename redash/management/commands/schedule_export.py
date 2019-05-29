import json
import logging

from django.conf import settings
from redash.models.jobs import Jobs
from redash.models.exports import Exports
from django.core.management.base import BaseCommand
from redash.services.redash_client import RedashClient

class Command(BaseCommand):
    help = 'Schedule Export'

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = RedashClient(
            api_key=settings.REDASH.get('api_key'),
            host=settings.REDASH.get('host')
        )

    def add_arguments(self, parser):
        parser.add_argument('-i', '--job_id', type=int,
                            help='Job id for which the schedule has to run', )

    def handle(self, *args, **kwargs):
        self.logger.info('Cron Started')
        if kwargs['job_id'] is not None:
            jobs = Jobs.objects.filter(id=kwargs['job_id'])
        else:
            jobs = Jobs.objects.filter(is_active=True)

        for job in jobs:
            export_id = self.request_export(job)
            self.insert_export_to_database(job, export_id)
            self.logger.info(export_id)

    def request_export(self, job):
        self.logger.info(f'Requesting New Results for the Job {job}')
        query_id = str(job.query_id)
        params = json.loads(job.parameters)

        sanitized_params = {}
        for key in params.keys():
            sanitized_params['p_' + key] = params.get(key)

        try:
            response = self.client.post(
                f'queries/{query_id}/refresh', payload=sanitized_params)
            return response['job']['id']
        except Exception as e:
            self.logger.error(e)

    def insert_export_to_database(self, job, export_id):
        if export_id is None:
            return

        export = Exports(
            job=job,
            query_job_id=export_id,
            query_status='INITIATED',
            status='PENDING'
        )
        export.save()
