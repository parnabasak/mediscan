from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *

admin.site.unregister(Group)

class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'date_created')
    search_fields = ('name', 'phone', 'address')
    list_filter = ('date_created',)

class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'home_service_available')
    search_fields = ('name', 'price', 'home_service_available')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'date_created')
    search_fields = ('invoice',)
    list_filter = ('date_created',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 3

class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'test', 'serial', 'date_created')
    search_fields = ('invoice', 'test')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 3



class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('patient', 'total', 'paid', 'date_created')
    search_fields = ('patient',)
    list_filter = ('date_created',)
    inlines = [InvoiceItemInline, PaymentInline]



admin.site.register(Patient, PatientAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
admin.site.register(Payment, PaymentAdmin)



"""
Doctors
"""
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'date_joined')
    search_fields = ('name', 'phone', 'address')
    list_filter = ('date_joined',)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date', 'time', 'status')
    search_fields = ('doctor', 'patient', 'date', 'time', 'status')
    list_filter = ('date', 'time', 'status')

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date', 'time', 'status')
    search_fields = ('doctor', 'patient', 'date', 'time', 'status')
    list_filter = ('date', 'time', 'status')

class AppointmentPaymentAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'amount', 'date_created')
    search_fields = ('appointment', 'amount', 'date_created')
    list_filter = ('date_created',)

class AppointmentPaymentInline(admin.TabularInline):
    model = AppointmentPayment
    extra = 3

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time')
    search_fields = ('day', 'start_time', 'end_time')
    list_filter = ('day', 'start_time', 'end_time')




admin.site.register(Speciality, SpecialityAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(AppointmentPayment, AppointmentPaymentAdmin)
admin.site.register(Schedule, ScheduleAdmin)
