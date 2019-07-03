import os
import json
import logging
from datetime import datetime, timedelta

from django.template import loader
from django.shortcuts import redirect
from django.utils.encoding import smart_str
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required

from redash.models.exports import Exports
from redash.models.export_logs import ExportLogs

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def all(request):
    exports = Exports.objects.all().order_by('-created_at')
    template = loader.get_template('allexports.html')
    export_for_view = []
    for export in exports:
        export.created_at += timedelta(minutes=330)
        if export.query_completed_at is not None:
            export.query_completed_at += timedelta(minutes=330)
        export_for_view.append(export)

    viewData = {
        'exports': export_for_view
    }
    return HttpResponse(template.render(viewData, request))


@login_required
def edit(request, id):
    export = Exports.objects.get(id=id)
    export.created_at += timedelta(minutes=330)
    if export.query_completed_at is not None:
        export.query_completed_at += timedelta(minutes=330)

    export_logs = ExportLogs.objects.filter(
        export_id=id).order_by('-created_at')

    export_logs_for_view = []
    for export_log in export_logs:
        export_log.created_at += timedelta(minutes=330)
        export_logs_for_view.append(export_log)

    template = loader.get_template('editexports.html')
    viewData = {
        'id': id,
        'export': export,
        'export_logs': export_logs_for_view
    }
    return HttpResponse(template.render(viewData, request))


@login_required
def download(request, id):
    export = Exports.objects.get(id=id)
    if not os.path.exists(export.file_name):
        raise Http404

    with open(export.file_name, 'rb') as fh:
        response = HttpResponse(
            fh.read(), content_type="application/octetstream")
        response['Content-Disposition'] = 'inline; filename=' + \
            os.path.basename(export.file_name)

        return response


@login_required
def save(request, id):
    export = Exports.objects.get(id=id)
    export.status = 'PENDING'
    export.save()

    export_logs = ExportLogs.objects.filter(export_id=id)
    export_logs.delete()

    return redirect('allexports')


@login_required
def delete(request, id):
    Exports.objects.filter(id=id).delete()
    return redirect('allexports')
