from typing import Iterable, Optional
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Patient(models.Model):
    user = models.OneToOneField(User, related_name='patient', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.name
    
class Test(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    home_service_available = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    total = models.FloatField( default=0, null=True, blank=True)
    paid = models.FloatField(default=0, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    home_service = models.BooleanField(default=False)
    home_service_date = models.DateField(null=True, blank=True)
    home_service_time = models.TimeField(null=True, blank=True)
       
    def __str__(self):
        return self.patient.name
    
    def save(self, *args, **kwargs):
        self.update_total()
        self.update_payment()
        super().save(*args, **kwargs)

    def status(self):
        for item in self.items.all():
            if item.status == 'Pending':
                return 'Pending'
        for item in self.items.all():
            if item.status == 'Specimen Collected':
                return 'Specimen Collected'
        return 'Report Ready'


    def update_total(self):
        try:
            self.total = 0
            for item in self.items.all():
                self.total += item.test.price
            for payment in self.payments.all():
                self.paid += payment.amount
        except:
            self.total = 0

    def update_payment(self):
        try:
            self.paid = 0
            for payment in self.payments.all():
                self.paid += payment.amount
        except:
            self.paid = 0

    def is_paid(self):
        if self.paid >= self.total:
            return True
        else:
            return False
        
    def due_amount(self):
        return self.total - self.paid
            
    
class InvoiceItem(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Specimen Collected', 'Specimen Collected'),
        ('Report Ready', 'Report Ready')
    )
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True, choices=STATUS, default='Pending')
    report = models.FileField(upload_to='reports/', null=True, blank=True)
    serial = models.IntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    date_report_uploaded = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.test.name
    
    def save(self, *args, **kwargs):
        self.invoice.update_total()
        if self.report:
            self.status = 'Report Ready'
            self.date_report_uploaded = timezone.now()
            if not self.date_completed:
                self.date_completed = timezone.now()
        if self.status == 'Completed':
            self.date_completed = timezone.now()
        self.invoice.update_total()
        if not self.serial:
            invoices = InvoiceItem.objects.filter(date_created = self.date_created)
            print(invoices)
            self.serial = invoices.filter(test=self.test).count() + 1


        super().save(*args, **kwargs)
    

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('bKash', 'bKash'),
        ('Rocket', 'Rocket'),
        ('Nagad', 'Nagad'),
    )
    invoice = models.ForeignKey(Invoice, related_name='payments', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    method = models.CharField(max_length=100, null=True, blank=True, choices=PAYMENT_METHODS)
    account = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.invoice.patient.name
    
    def save(self, *args, **kwargs):
        self.invoice.update_payment()
        super().save(*args, **kwargs)




"""
Doctor and scheduling
"""

class Speciality(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = self.slug if self.slug else self.name.replace(' ', '-').replace('/','-').lower()
        super(Speciality, self).save(*args, **kwargs)
    

class Schedule(models.Model):
    DAYS = (
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday','Friday'),
    )
    
    day = models.CharField(max_length=100, choices=DAYS, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.day + ': ' + str(self.start_time) + ' to ' + str(self.end_time)


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    workplace = models.CharField(max_length=100, default="N/A")
    degree = models.CharField(max_length=100, null=True, blank=True)
    speciality = models.ForeignKey(Speciality, related_name='doctors', on_delete=models.SET_NULL, null=True)
    bmdc = models.IntegerField()
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/doctors/', null=True, blank=True)
    schedules = models.ManyToManyField(Schedule, blank=True)
    fees = models.IntegerField()
    bio = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name
    


class Appointment(models.Model):
    
    STATUS = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    
    patient = models.ForeignKey(Patient, related_name='appointments', on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey(Doctor, related_name='appointments', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=100, choices=STATUS, null=True, default='Confirmed')
    note = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.patient.name + ' - ' + self.doctor.name + ' - ' + str(self.date) + ' - ' + str(self.time)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def is_paid(self):
        try:
            total = 0
            for payment in self.payments.all():
                total += payment.amount
            if total >= self.doctor.fees:
                return True
            else:
                return False
        except:
            return False

    

class AppointmentPayment(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('bKash', 'bKash'),
        ('Rocket', 'Rocket'),
        ('Nagad', 'Nagad'),
    )
    appointment = models.ForeignKey(Appointment, related_name='payments', on_delete=models.CASCADE, null=True, blank=True)
    method = models.CharField(max_length=100, null=True, blank=True, choices=PAYMENT_METHODS)
    amount = models.FloatField(null=True, blank=True)
    account = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f'{self.appointment.patient.name} - {self.amount}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
