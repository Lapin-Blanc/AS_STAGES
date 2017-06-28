#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.utils import timezone
from django.contrib.auth.models import User, Permission
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, F

MIN_DELAY = 7 # le délai minimum pour encodage 

# Create your models here.
class Supervisor(User):
    simple_password = models.CharField("mot de passe", max_length=20)
    phone = models.CharField("téléphone", max_length=20, blank=True, default="")

    def save(self, *args, **kwargs):
        super(Supervisor, self).save(*args, **kwargs)
        self.user_ptr.set_password(self.simple_password)
        self.user_ptr.is_staff = True
        self.user_ptr.user_permissions=Permission.objects.filter(Q(codename__contains='traineeship')|Q(codename__contains='student'))
        self.user_ptr.save()

    class Meta:
        verbose_name = "Superviseur"

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name,)

class Student(User):
    simple_password = models.CharField("mot de passe", max_length=20)
    phone = models.CharField("téléphone", max_length=20, blank=True, default="")

    def save(self, *args, **kwargs):
        super(Student, self).save(*args, **kwargs)
        self.user_ptr.set_password(self.simple_password)
        self.user_ptr.is_staff = True
        self.user_ptr.user_permissions=Permission.objects.filter(Q(codename='change_traineeship')|Q(codename='add_traineeship'))
        self.user_ptr.save()

    class Meta:
        verbose_name = "élève"

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name,)


class Traineeship(models.Model):
    TS_CAT = (
        ("observation","Observation"),
        ("insertion","Insertion"),
        ("intégration","Intégration"),
    )
    category = models.CharField("type", max_length=20, choices = TS_CAT, default = TS_CAT[0][0])
    student = models.ForeignKey("Student", verbose_name="étudiant", related_name="traineeships")
    supervisor = models.ForeignKey("Supervisor", verbose_name="superviseur", related_name="traineeships")
    place = models.CharField("emplacement", max_length=100)
    date_start = models.DateField("date de début", default=timezone.localdate()+timezone.timedelta(days=MIN_DELAY))
    date_end = models.DateField("date de fin", null=True, blank=True)
    is_closed = models.BooleanField("cloturé", default=False)

    def hour_duration(self):
        ps = self.periods.all()
        duration = 0.
        for p in ps:
            duration += p.hour_duration()
        return duration
    hour_duration.short_description = "Durée en heures"
    
    def period_duration(self):
        return self.hour_duration() * 6/5
    period_duration.short_description = "Durée en périodes"

    def clean(self):
        # we check that end date_end is not before date_start
        if self.date_end and self.date_end < self.date_start:
            raise ValidationError(
                'La date de fin %(date_end)s est avant la date de début %(date_start)s',
                code = 'invalid',
                params = {'date_start':self.date_start, 'date_end':self.date_end}
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(Traineeship, self).save()

    class Meta:
        verbose_name = "Stage"

    def __str__(self):
        return "%s - Stage d'%s" % (self.student, self.category)


class Period(models.Model):
    traineeship = models.ForeignKey(Traineeship, related_name = "periods", on_delete=models.CASCADE)
    start = models.DateTimeField("début")
    end = models.DateTimeField("fin")
    date_created = models.DateTimeField("Date de création", auto_now_add=True)
    date_modified = models.DateTimeField("Date de modification", auto_now=True)

    def hour_duration(self):
        delta = self.end - self.start
        return delta.seconds / 3600
    hour_duration.short_description = "Durée en heures"

    def period_duration(self):
        return self.hour_duration() * 6/5
    period_duration.short_duration = "Durée en périodes"

    def clean(self):
        # we check that end is not equal or before end
        if self.end <= self.start:
            raise ValidationError(
                "L'heure de fin $(end) est antérieure à l'heure de fin $(start) !",
                code = 'invalid',
                params = {'start':self.sart, 'end':self.end}
            )
        # we check that this period is not overlapping an existing one
        qs1 = Period.objects.exclude(id=int(self.id or -1)).filter(traineeship=self.traineeship, start__gte=self.start, start__lte=self.end)
        qs2 = Period.objects.exclude(id=int(self.id or -1)).filter(traineeship=self.traineeship, end__gte=self.start, end__lte=self.end)
        if qs1 or qs2:
            raise ValidationError(
                "Les périodes ne peuvent pas se toucher ou se chevaucher",
                code = 'invalid'
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(Period, self).save()

    class Meta:
        verbose_name = "période"
        ordering = ['-start']

    def __str__(self):
        return "%s -> %s" % (self.start.strftime("%d/%m/%Y %H:%M"), self.end.strftime("%d/%m/%Y %H:%M"))
