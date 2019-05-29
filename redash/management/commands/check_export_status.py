import csv
import json
import logging
import datetime
import xlsxwriter

from io import StringIO
from django.conf import settings
from redash.models.jobs import Jobs
from redash.models.exports import Exports
from redash.services.sftp import SFTPFacade
from redash.services.email import MailFacade
from redash.services.storage import StorageFacade
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
        self.storage = StorageFacade().get_instance()
        self.mail = MailFacade().get_instance()
        self.sftp = SFTPFacade().get_instance()

    def add_arguments(self, parser):
        parser.add_argument('-e', '--export_id', type=int,
                            help='Job id for which the schedule has to run')

        parser.add_argument('-s', '--status',
                            help='Job status for which the schedule has to run')

    def handle(self, *args, **kwargs):
        self.logger.info('Export Status Cron Started')
        status = 'PENDING'
        if kwargs['status'] is not None:
            status = kwargs['status']

        exports = Exports.objects.filter(status=status)
        for export in exports:
            query_execution_response = self.check_query_status_in_redash(
                export)
            if query_execution_response is None:
                self.logger.info(f'Export {export.id} is still running..')
                continue

            if export.status == 'PENDING':
                export.status = 'EXECUTED'
                export.save()

            if export.status == 'EXECUTED':
                if export.job.is_excel_required:
                    export.file_name = self.get_export_result_as_excel(
                        export, query_execution_response)
                else:
                    export.file_name = self.get_export_result_as_csv(
                        export, query_execution_response)

                export.status = 'DOWNLOADED'
                export.save()

            if export.status == 'DOWNLOADED':
                self.push_query_result_to_s3(export, query_execution_response)
                export.status = 'SAVED_TO_STORAGE'
                export.save()

            if export.status == 'SAVED_TO_STORAGE':
                self.mail_query_result(export, query_execution_response)
                export.status = 'MAILED'
                export.save()

            if export.status == 'MAILED':
                self.push_query_result_to_sftp(export, query_execution_response)
                export.status = 'PUSHED_TO_SFTP'
                export.save()

    def check_query_status_in_redash(self, export):
        self.logger.info(
            f'Polling Job Id {export.query_job_id} to check for a resolution')

        response = self.client.get(f'jobs/{export.query_job_id}')
        self.logger.info(f'Response from the Redash Server is: {response}')

        if response['job']['status'] != 3:
            return None

        return response

    def get_export_result_as_csv(self, export, query_execution_response):
        result_id = query_execution_response['job']['query_result_id']
        url = f'queries/{export.job.query_id}/results/{result_id}.json'
        self.logger.debug(f'Making an API call to the URL {url}')
        response = self.client.get(url)

        res = response['query_result']['data']['rows']
        file_date =  datetime.datetime.now()
        file_name = f'results-{export.job.query_name}-{file_date}.csv'
        with open(file_name, 'w') as f:
            w = csv.DictWriter(f, res[0].keys())
            w.writeheader()
            w.writerows(res)

        return file_name

    def get_export_result_as_excel(self, export, query_execution_response):
        result_id = query_execution_response['job']['query_result_id']
        url = f'queries/{export.job.query_id}/results/{result_id}.json'
        self.logger.debug(f'Making an API call to the URL {url}')
        response = self.client.get(url)

        file_date =  datetime.datetime.now()
        file_name = f'results-{export.job.query_name}-{file_date}.xlsx'
        query_data = response['query_result']['data']
        book = xlsxwriter.Workbook(file_name, {
            'constant_memory': True,
            'strings_to_urls': False
        })
        sheet = book.add_worksheet('Export Data')

        column_names = []
        for (c, col) in enumerate(query_data['columns']):
            sheet.write(0, c, col['name'])
            column_names.append(col['name'])

        for (r, row) in enumerate(query_data['rows']):
            for (c, name) in enumerate(column_names):
                v = row.get(name)
                if isinstance(v, list) or isinstance(v, dict):
                    v = str(v).encode('utf-8')
                sheet.write(r + 1, c, v)

        book.close()
        return file_name

    def push_query_result_to_s3(self, export, query_execution_response):
        self.storage.save(export.file_name)

    def mail_query_result(self, export, query_execution_response):
        attachments = [
            export.file_name
        ]
        self.mail.send_mail(recipients=export.job.configured_emails.split(
            ';'), attachments=attachments)

    def push_query_result_to_sftp(self, export, query_execution_response):
        file_name = export.file_name
        self.sftp.create_connection(
            hostname=export.job.sftp_host,
            port=22,
            username=export.job.sftp_username,
            password=export.job.sftp_password
        )

        self.sftp.put_file(file_name, remote_folder=export.job.sftp_path)
