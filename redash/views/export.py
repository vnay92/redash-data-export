import json
import logging

from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


from redash.models.exports import Exports
from redash.models.export_logs import ExportLogs

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def all(request):
    exports = Exports.objects.all().order_by('-created_at')
    template = loader.get_template('allexports.html')
    viewData = {
        'exports': exports
    }
    return HttpResponse(template.render(viewData, request))


@login_required
def edit(request, id):
    export = Exports.objects.filter(id=id)
    export_logs = ExportLogs.objects.filter(export_id=id)
    template = loader.get_template('editexports.html')
    viewData = {
        'id': id,
        'export': export,
        'export_logs': export_logs
    }
    return HttpResponse(template.render(viewData, request))


@login_required
def save(request, id):
    export = Exports.objects.get(id=id)
    export.status = 'PENDING'
    export.save()
    return redirect('allexports')


@login_required
def delete(request, id):
    Exports.objects.filter(id=id).delete()
    return redirect('allexports')
