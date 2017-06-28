from django.contrib import admin
from .models import Supervisor, Student, Traineeship, Period
from django.core.exceptions import ValidationError

from django import forms

# Register your models here.

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    fields = ['username', 'first_name', 'last_name', 'email', 'phone','simple_password',]
    list_display = ['username', 'first_name', 'last_name', 'email', 'phone','simple_password',]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    fields = ['username', 'first_name', 'last_name', 'email', 'phone','simple_password',]
    list_display = ['username', 'first_name', 'last_name', 'email', 'phone','simple_password',]


@admin.register(Traineeship)
class TraineeshipAdmin(admin.ModelAdmin):
    list_display = ['place', 'supervisor', 'category', 'student', 'date_start', 'hour_duration', 'period_duration', 'is_closed']

    def get_readonly_fields(self, request, obj=None):
        # first, we check if we are student
        try:
            request.user.student
            # then if we are editing an existing traineeship
            if obj:
                # if yes, then everything is read only for students
                return ['supervisor', 'category', 'date_start','place', 'is_closed']
            # we're encoding a new traineeship
            else:
                return ['is_closed',]
        # we're admin or supervisor
        except Student.DoesNotExist:
            # if we are admin or supervisor, everything can ben modified except student !
            if obj:
                return ['student']
            else:
                return []

    def get_fields(self, request, obj):
        try:
            request.user.student
            return ['supervisor', 'category', 'place', 'date_start', 'is_closed']
        except Student.DoesNotExist:
            return ['student', 'supervisor', 'category', 'place', 'date_start', 'is_closed']
            
    def save_model(self, request, obj, form, change):
        try:
            s = request.user.student
            obj.student = s
        except Student.DoesNotExist:
            pass
        super(TraineeshipAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(TraineeshipAdmin, self).get_queryset(request)
        try:
            s =  request.user.student
            return qs.filter(student=s)
        # we're admin or teacher
        except Student.DoesNotExist:
            return qs
        

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['traineeship', 'start', 'end', 'date_created', 'date_modified', 'hour_duration', 'period_duration']
