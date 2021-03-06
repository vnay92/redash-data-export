import json
import logging

from redash.models.jobs import Jobs
from redash.services.scheduler.Scheduler import Scheduler

from datetime import datetime, timedelta
from dateutil.parser import parse

from django.utils import timezone
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.management import call_command
from django.contrib.auth.decorators import login_required

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def all(request):
    jobs = Jobs.objects.all().order_by('-created_at')
    template = loader.get_template('alljobs.html')
    jobs_for_view = []

    for job in jobs:
        if job.schedule_start_time is not None:
            job.schedule_start_time += timedelta(minutes=330)

        if job.schedule_end_time is not None:
            job.schedule_end_time += timedelta(minutes=330)
        jobs_for_view.append(job)

    viewData = {
        'jobs': jobs_for_view
    }
    return HttpResponse(template.render(viewData, request))


@login_required
def new(request):
    template = loader.get_template('newjob.html')
    viewData = None
    return HttpResponse(template.render(viewData, request))


@login_required
def create(request):
    data = request.POST
    logger.info(f'Data from Request {json.dumps(data)}')

    job = Jobs()
    job.query_id = data.get('query_id')
    job.is_active = (data.get('is_active') ==
                     '' or data.get('is_active') == 'on')

    job.query_name = data.get('query_name')
    job.parameters = data.get('parameters')
    job.configured_emails = data.get('configured_emails')

    if data.get('schedule') != '':
        job.schedule = data.get('schedule')
    else:
        job.schedule = 1 * 24 # Every day

    job.is_excel_required = (data.get('is_excel_required')
                             == '' or data.get('is_excel_required') == 'on')

    job.is_sftp_used = (data.get('is_sftp_used') ==
                        '' or data.get('is_sftp_used') == 'on')

    job.should_be_zipped = (data.get('should_be_zipped') ==
                            '' or data.get('should_be_zipped') == 'on')

    job.sftp_username = data.get('sftp_username')
    job.sftp_host = data.get('sftp_host')
    job.sftp_password = data.get('sftp_password')
    job.sftp_path = data.get('sftp_path')
    job.added_by = request.user
    job.last_edited_by = request.user
    job.csv_delimiter = data.get('csv_delimiter')

    job.columns_order = data.get('columns_order')

    if data.get('schedule_start_time'):
        job.schedule_start_time = parse(
            data.get('schedule_start_time')) - timedelta(minutes=330)
    else:
        job.schedule_start_time = timezone.now()

    if data.get('schedule_end_time'):
        job.schedule_end_time = parse(
            data.get('schedule_end_time')) - timedelta(minutes=330)
    else:
        job.schedule_end_time = timezone.now()

    job.save()

    if data.get('is_scheduled'):
        Scheduler.add_job(job)
        return redirect('alljobs')

    call_command('schedule_export', job_id=job.pk)
    return redirect('alljobs')


@login_required
def edit(request, id):
    job = Jobs.objects.get(id=id)
    template = loader.get_template('editjob.html')

    if job.schedule_start_time is None:
        job.schedule_start_time = timezone.now()

    if job.schedule_end_time is None:
        job.schedule_end_time = timezone.now()

    viewData = {
        'id': id,
        'job': job,
        'schedule_start_time': (job.schedule_start_time + timedelta(minutes=330)).strftime("%Y-%m-%dT%H:%M:%S"),
        'schedule_end_time': (job.schedule_end_time + timedelta(minutes=330)).strftime("%Y-%m-%dT%H:%M:%S"),
    }
    return HttpResponse(template.render(viewData, request))


@login_required
def save(request, id):
    data = request.POST
    logger.info(f'Data from Request {data}')
    job = Jobs.objects.get(id=id)

    job.query_id = data.get('query_id')
    job.is_active = (data.get('is_active') ==
                     '' or data.get('is_active') == 'on')

    job.query_name = data.get('query_name')
    job.parameters = data.get('parameters')
    job.configured_emails = data.get('configured_emails')

    if data.get('schedule') != '':
        job.schedule = data.get('schedule')
    else:
        job.schedule = 1

    job.is_excel_required = (data.get('is_excel_required')
                             == '' or data.get('is_excel_required') == 'on')
    job.is_sftp_used = (data.get('is_sftp_used') ==
                        '' or data.get('is_sftp_used') == 'on')

    job.should_be_zipped = (data.get('should_be_zipped') ==
                        '' or data.get('should_be_zipped') == 'on')

    job.sftp_username = data.get('sftp_username')
    job.csv_delimiter = data.get('csv_delimiter')
    job.sftp_host = data.get('sftp_host')
    job.sftp_password = data.get('sftp_password')
    job.sftp_path = data.get('sftp_path')
    job.last_edited_by = request.user

    job.columns_order = data.get('columns_order')

    job.schedule_start_time = parse(
        data.get('schedule_start_time')) - timedelta(minutes=330)

    job.schedule_end_time = parse(
        data.get('schedule_end_time')) - timedelta(minutes=330)

    job.save()

    try:
        Scheduler.remove_job(job.id)
        Scheduler.add_job(id=id)
    except:
        pass

    return redirect('alljobs')


@login_required
def delete(request, id):
    job = Jobs.objects.get(id=id)
    try:
        Scheduler.remove_job(job.id)
    except:
        pass

    Jobs.objects.filter(id=id).delete()
    return redirect('alljobs')
