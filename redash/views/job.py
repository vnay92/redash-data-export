import json
import logging

from redash.models.jobs import Jobs
from redash.services.scheduler import Scheduler

from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.management import call_command
from django.contrib.auth.decorators import login_required


# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def all(request):
    jobs = Jobs.objects.all()
    template = loader.get_template('alljobs.html')
    viewData = {
        'jobs': jobs
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
    job.is_active = (data.get('is_active') == '')
    job.query_name = data.get('query_name')
    job.parameters = data.get('parameters')
    job.configured_emails = data.get('configured_emails')
    job.schedule = data.get('schedule')
    job.is_excel_required = (data.get('is_excel_required') == '')
    job.is_sftp_used = (data.get('is_sftp_used') == '')
    job.sftp_username = data.get('sftp_username')
    job.sftp_host = data.get('sftp_host')
    job.sftp_password = data.get('sftp_password')
    job.sftp_path = data.get('sftp_path')
    job.added_by = request.user
    job.last_edited_by = request.user
    job.save()

    if data.get('is_scheduled'):
        Scheduler.add_job(job)

    call_command('schedule_export', id=job.pk)
    return redirect('alljobs')


@login_required
def edit(request, id):
    job = Jobs.objects.get(id=id)
    template = loader.get_template('editjob.html')
    viewData = {
        'id': id,
        'job': job
    }
    return HttpResponse(template.render(viewData, request))


@login_required
def save(request, id):
    data = request.POST
    logger.info(f'Data from Request {data}')
    job = Jobs.objects.get(id=id)

    job.query_id = data.get('query_id')
    job.is_active = (data.get('is_active') == '')
    job.query_name = data.get('query_name')
    job.parameters = data.get('parameters')
    job.configured_emails = data.get('configured_emails')
    job.schedule = data.get('schedule')
    job.is_excel_required = (data.get('is_excel_required') == '')
    job.is_sftp_used = (data.get('is_sftp_used') == '')
    job.sftp_username = data.get('sftp_username')
    job.sftp_host = data.get('sftp_host')
    job.sftp_password = data.get('sftp_password')
    job.sftp_path = data.get('sftp_path')
    job.last_edited_by = request.user

    job.save()

    Scheduler.remove_job(job.id)
    Scheduler.add_job(id=id)

    return redirect('alljobs')


@login_required
def delete(request, id):
    Jobs.objects.filter(id=id).delete()
    Scheduler.remove_job(id)
    return redirect('alljobs')
