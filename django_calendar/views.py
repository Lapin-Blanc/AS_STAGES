#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import dateparse, timezone
from .models import Period, Traineeship, Student
from django.core.exceptions import ValidationError

from datetime import datetime, date

from io import BytesIO
from docx import Document

def json_access_error(request):
     return  JsonResponse(
                {
                  "errors": [
                    {
                      "status": "403",
                      "source": { "pointer": request.path },
                      "detail": "vous n'êtes plus autorisé à utiliser cette période"
                    },
                  ]
                },
                status=403
            )
 
def time_limit():
    today = timezone.localdate()
    days_offset = 3-today.weekday()
    return timezone.make_aware(datetime.combine(today+timezone.timedelta(days=days_offset), datetime.min.time()))

def calendar(request, action, traineeship):
    user = request.user
    traineeship = Traineeship.objects.get(id=int(traineeship))
    try:
        student = user.student
    except Student.DoesNotExist:
        student = None

    # calendar read
    if action=='read':
        time_start = timezone.make_aware(datetime.combine(dateparse.parse_date(request.GET['start']), datetime.min.time()))
        time_end = timezone.make_aware(datetime.combine(dateparse.parse_date(request.GET['end']), datetime.min.time()))
        base_criteria = {
            'traineeship' : traineeship
        }
        if request.GET['type']=='past':
            base_criteria['start__gte'] = time_start
            base_criteria['end__lt'] = time_limit()

        if request.GET['type']=='future':
            base_criteria['start__gte'] = time_limit()
            base_criteria['end__lt'] = time_end
        ps = Period.objects.filter(**base_criteria)
        d = []
        for p in ps:
            d.append({
                    'id': p.id,
                    'start': p.start,
                    'end': p.end,
            })
        return JsonResponse(d, safe=False)

    # create period
    if action=='create':
        time_start = dateparse.parse_datetime(request.GET['start'])
        time_end = dateparse.parse_datetime(request.GET['end'])
        if student and time_start<time_limit():
            return json_access_error(request)            
        try:
            p = traineeship.periods.create(start=time_start, end=time_end)
            return JsonResponse({"event_id" : p.id}, safe=False)
        except ValidationError as e:
            return JsonResponse(
                {
                  "errors": [
                    {
                      "status": "422",
                      "source": { "pointer": request.path },
                      "detail": "%s" % e.args[0]
                    },
                  ]
                },
                status=422
            )
    
    # delete event
    if action=='delete':
        p = traineeship.periods.get(id=int(request.GET['event_id']))
        if student and p.start<time_limit():
            return json_access_error(request)            
        p.delete()
        return JsonResponse({"event_id" : 0}, safe=False)
        
    # update event
    if action=='update':
        try:
            p = traineeship.periods.get(id=int(request.GET['event_id']))
            time_start = dateparse.parse_datetime(request.GET['start'])
            time_end = dateparse.parse_datetime(request.GET['end'])
            if student and time_start<time_limit():
                return json_access_error(request)            
            p.start = time_start
            p.end = time_end
            p.save()
            return JsonResponse({"event_id" : p.id}, safe=False)

        except ValidationError as e:
            return JsonResponse(
                {
                  "errors": [
                    {
                      "status": "422",
                      "source": { "pointer": request.path },
                      "detail": "%s" % e.args[0]
                    },
                  ]
                },
                status=422
            )
    # On ne devrait pas arriver ici...
    return JsonResponse(
        {
            "errors": [
                {
                    "status": "400",
                    "source": { "pointer": request.path },
                    "detail": "action not found"
                },
            ]
        },
        status=400
     )


# DOCX
def download_schedule(request, traineeship):
    user = request.user
    ts = Traineeship.objects.get(id=int(traineeship))
    try:
        student = user.student
    except Student.DoesNotExist:
        student = None

    # Create the HttpResponse object with the appropriate docx headers.
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="horaire.docx"'

    buffer = BytesIO()

    document = Document()
    document.add_heading("%s %s : Stage d'%s" % (ts.student.first_name, ts.student.last_name, ts.category), 0)

    document.save(buffer)
    # Get the value of the BytesIO buffer and write it to the response.
    doc = buffer.getvalue()
    buffer.close()
    response.write(doc)
    return response 
