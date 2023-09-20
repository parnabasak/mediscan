from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.db.models import Q
import json
from datetime import datetime, timedelta
from django.utils import timezone


# Create your views here.

def index(request):
    return render(request, 'index/index.html')

def register(request):
    data = {}
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            email = request.POST.get('email')
            username = email.split('@')[0]
            password = request.POST.get('password')
            password2 = request.POST.get('confirm_password')
            if password != password2:
                raise Exception('Password does not match')
            if User.objects.filter(email=email).exists():
                raise Exception('User with this email already exists')
            if User.objects.filter(username=username).exists():
                username+=str(User.objects.count())
            user = User.objects.create_user(username=username, password=password)
            user.email = email
            user.save()
            
            patient = Patient.objects.create(user=user, name=name, phone=phone, address=address)
            patient.save()
            login(request, user)            
            return redirect('/')
    except Exception as e:
        data['error'] = 'Error: ' + str(e)
    
    return render(request, 'index/register.html', data)


def loginPage(request):
    data = {}
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            username = User.objects.get(email=email).username
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                data['error'] = 'Error: Something went wrong'
    except Exception as e:
        data['error'] = 'Error: Username or password is incorrect'
            
    return render(request, 'index/login.html', data)



def logoutUser(request):
    if request.method == 'POST':
        if request.user.is_authenticated and request.POST.get('action') == 'logout':
            logout(request)
            return redirect('index')
    return render(request, 'index/logout.html')



def user_profile(request):
    data = {'title': 'My Profile'}
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        email = request.POST.get('email')
        request.user.email = email
        request.user.save()
        request.user.patient.name = name
        request.user.patient.phone = phone
        request.user.patient.address = address
        request.user.patient.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('user_home')
    return render(request, 'user/profile.html', data)


def user_appointments(request):
    data = {'title': 'My Appointments', 'sub_title': 'pending or confirmed appointments'}
    data['appointments'] = Appointment.objects.filter(patient=request.user.patient, status__in=['Pending', 'Confirmed'])
    return render(request, 'user/appointments.html', data)


def user_appointments_archived(request):
    data = {'title': 'Archived Appointments', 'sub_title': 'completed or cancelled appointments'}
    data['appointments'] = Appointment.objects.filter(patient=request.user.patient, status__in=['Completed', 'Cancelled'])

    return render(request, 'user/appointments.html', data)


def user_invoices(request):
    data = {'title': 'My Invoices', 'sub_title': 'All invoices'}
    data['invoices'] = Invoice.objects.filter(patient=request.user.patient).order_by('-pk')
    return render(request, 'user/invoice_list.html', data)

def user_create_invoice(request, patient):
    patient = update_patient(request, patient)
    invoice = Invoice.objects.create(patient=patient)
    invoice.home_service = True
    invoice.home_service_date = request.POST.get('date')
    invoice.home_service_time = request.POST.get('time')
    invoice.save()
    for test_id in request.POST.getlist('tests'):
        invoice_item = InvoiceItem.objects.create(invoice=invoice, test_id=test_id)
        invoice_item.save()
    invoice.save()
    return f'Home service requested successfully. Click <a href="/user/invoices/{str(invoice.id)}">here</a> to view invoice.'




def user_invoice_create(request):
    data = {'title': 'Book Test at Home', 'tests': Test.objects.filter(home_service_available=True)}
    try:
        data['patient']= Patient.objects.get(user=request.user)
    except:
        pass
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone')
            patient = Patient.objects.get(phone=phone)
            data['success'] = user_create_invoice(request, patient)
        except Patient.DoesNotExist:
            patient = create_patient(request)
            data['success'] = user_create_invoice(request, patient)
        except Exception as e:
            data['error'] = str(e)
    return render(request, 'user/invoice_create.html', data)


def user_invoice_detail(request, pk):
    data = {'title': 'Invoice Detail'}
    try:
        data['invoice'] = Invoice.objects.get(pk=pk)        
    except:
        data['error'] = 'Error: Invoice not found'
    return render(request, 'user/invoice_detail.html', data)





"""
Tests Listing
"""

def services(request):
    data = {}
    data['tests'] = Test.objects.all()
    return render(request, 'index/services.html', data)


def doctors(request):
    data = {}
    data['specialities'] = Speciality.objects.all()
    return render(request, 'index/doctors.html', data)


def calculateSchedule(request, doctor):
    data = {'dates': {}, 'doctor': doctor}
    for i in range(0, 30):
        day = (datetime.now() + timedelta(days=i)).strftime('%A')
        days = [schedule.day for schedule in data['doctor'].schedules.all()]
        if day in days:
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            data['dates'][date] = {}
            data['dates'][date]['date'] = (datetime.now() + timedelta(days=i)).strftime('%d %B, %Y')
            data['dates'][date]['day'] = (datetime.now() + timedelta(days=i)).strftime('%A')
            data['dates'][date]['slots'] = {}
            start_time = datetime.strptime(str(data['doctor'].schedules.get(day=day).start_time), '%H:%M:%S')
            end_time = datetime.strptime(str(data['doctor'].schedules.get(day=day).end_time), '%H:%M:%S')
            while start_time < end_time:
                time = start_time.strftime('%I:%M %p')
                #convert this to django timefield
                converted_time = datetime.strptime(time, '%I:%M %p').time()
                if Appointment.objects.filter(doctor=data['doctor'], date=date, time=converted_time).count() > 0:
                    data['dates'][date]['slots'][start_time.strftime('%I:%M %p')] = 'booked'
                    
                else:
                    data['dates'][date]['slots'][start_time.strftime('%I:%M %p')] = 'open'
                    # data['dates'][date]['slots'][start_time.strftime('%I:%M %p')] = [start_time, 'open']                    
                start_time = start_time + timedelta(minutes=15)
            data['dates'][date]['slots'] = json.dumps(data['dates'][date]['slots'])
    return data['dates']


def bookAppointment(request, doctor):    
    data = {}
    try:
        patient = request.user.patient
        time = datetime.strptime(request.POST['time'], '%I:%M %p').time()
        date = datetime.strptime(request.POST['date'], '%Y-%m-%d').date()
        appointment = Appointment.objects.create(patient=patient, doctor=doctor, date=date, time=time)
        appointment.save()
        data['success'] = 'Appointment booked successfully'        
    except:
        data['error'] = 'Only a patient account can book an appointment'
    return data

def doctor_detail(request, pk):
    data = {}
    data['doctor'] = Doctor.objects.get(pk=pk)
    data['dates'] = calculateSchedule(request, data['doctor'])
    try:
        data['doctor'] = Doctor.objects.get(pk=pk)
        data['dates'] = calculateSchedule(request, data['doctor'])
    except:
        data['error'] = 'Error: Doctor not found'
        return render(request, 'index/doctor_detail.html', data)
    if request.method == 'POST':
        message = bookAppointment(request, data['doctor'])
        if 'error' in message:
            data['error'] = message['error']
        elif 'success' in message:
            data['success'] = message['success']

    return render(request, 'index/doctor_detail.html', data)


"""
Doctors and Appointments
"""





"""
Dashboard
"""

def dashboard_home(request):
    data = {'title': 'Dashboard'}
    #calculate total patients who joned this month
    patients = Patient.objects.all()
    total_patients = patients.count()
    total_patients_this_month = patients.filter(date_created__month=datetime.now().month).count()
    total_patients_last_month = patients.filter(date_created__month=datetime.now().month-1).count()
    try:
        change = (total_patients_this_month - total_patients_last_month) / total_patients_last_month * 100
    except ZeroDivisionError:
        change = 100
    data['patient'] = {
        'this_month': total_patients_this_month,
        'last_month': total_patients_last_month,
        'change': change,
    }

    #calculate total invoices
    invoices = Invoice.objects.all()
    total_invoices = invoices.count()
    total_invoices_this_month = invoices.filter(date_created__month=datetime.now().month).count()
    total_invoices_last_month = invoices.filter(date_created__month=datetime.now().month-1).count()
    try:
        change = (total_invoices_this_month - total_invoices_last_month) / total_invoices_last_month * 100
    except ZeroDivisionError:
        change = 100
    data['invoices'] = {
        'this_month': total_invoices_this_month,
        'last_month': total_invoices_last_month,
        'change': change,
    }

    #calculate total payments
    payments = Payment.objects.all()
    payments_this_month = payments.filter(date_created__month=datetime.now().month)
    amount = 0
    for payment in payments_this_month:
        amount += payment.amount
    payments_this_month = amount
    payments_last_month = payments.filter(date_created__month=datetime.now().month-1)
    amount = 0
    for payment in payments_last_month:
        amount += payment.amount
    payments_last_month = amount
    try:
        change = (payments_this_month - payments_last_month) / payments_last_month * 100
    except ZeroDivisionError:
        change = 100
    data['payments'] = {
        'this_month': payments_this_month,
        'last_month': payments_last_month,
        'change': change,
    }

    data['appointments'] = Appointment.objects.filter(date=datetime.now().date(), status__in=['Pending', 'Confirmed']).order_by('time')
    data['tests'] = InvoiceItem.objects.filter(date_created__date=datetime.now().date()).filter(status__in=['Pending', 'Completed']).order_by('date_created')
    if request.method == 'POST':
        if request.POST.get('action') == 'update_test':
            try:
                request.POST.get('test_id')
                test = InvoiceItem.objects.get(id=request.POST.get('test_id'))
                try:
                    if request.POST.get('test_done') == 'on':
                        test.status = 'Completed'
                except:
                    pass
                try:
                    test.report = request.FILES.get('report')
                except:
                    pass
                test.save()
            except Exception as e:
                pass              
                
                
    return render(request, 'dashboard/index.html', data)


def dashboard_patients(request):
    page = request.GET.get('page', 1)
    start = (page - 1) * 10
    end = page * 10
    patients = Patient.objects.all()
    if request.GET.get('name') is not None:
        patients = patients.filter(name__icontains=request.GET.get('name'))
    if request.GET.get('phone') is not None:
        patients = patients.filter(phone__icontains=request.GET.get('phone'))
    patients = patients[start:end]
    data = {
        'patients': patients,
        'page': page,
        'title': 'Patients List',
    }
    return render(request, 'dashboard/patient_list.html', data)

def dashboard_patient_detail(request, pk):
    patient = Patient.objects.get(id=pk)
    invoices = patient.invoice_set.all()
    data = {
        'patient': patient,
        'invoices': invoices,
        'title': 'Patient Detail',
    }
    return render(request, 'dashboard/patient_detail.html', data)

def dashboard_patient_edit(request, pk):
    patient = Patient.objects.get(id=pk)
    data = {
        'patient': patient,
        'title': 'Edit Patient',
    }
    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        patient.save()
        messages.success(request, 'Patient was updated successfully')
        return redirect('dashboard_patient_detail', pk=patient.id)
    return render(request, 'dashboard/patient_edit.html', data)


def dashboard_patient_delete(request, pk):
    patient = Patient.objects.get(id=pk)
    patient.delete()
    messages.success(request, 'Patient was deleted successfully')
    return redirect('dashboard_patien_list')



def create_patient(request):
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    username = email.split('@')[0]
    user = User.objects.create_user(username=username, password=phone)
    user.email = email
    user.save()
    patient = Patient.objects.create(user=user)
    patient.phone = phone
    patient.name = request.POST.get('name')
    patient.address = request.POST.get('address')
    patient.save()
    return patient

def update_patient(request, patient):
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    username = email.split('@')[0]
    user = patient.user
    user.username = username
    user.email = email
    user.save()
    patient.phone = request.POST.get('phone')
    patient.name = request.POST.get('name')
    patient.address = request.POST.get('address')
    patient.save()
    return patient

def create_invoice(request, patient):
    patient = update_patient(request, patient)
    invoice = Invoice.objects.create(patient=patient)
    invoice.save()
    for test_id in request.POST.getlist('tests'):
        invoice_item = InvoiceItem.objects.create(invoice=invoice, test_id=test_id)
        invoice_item.save()
    try:
        amount = request.POST.get('amount')
    except:
        amount = request.POST.get('total_bill')
    method = request.POST.get('method')
    try:
        account = request.POST.get('account')
    except:
        account = None
    payment = Payment.objects.create(invoice=invoice, amount=amount, method=method, account=account)
    payment.save()
    invoice.save()
    return f'Invoice was created successfully. Click <a href="/dashboard/invoices/{str(invoice.id)}">here</a> to view invoice.'


def dashboard_invoice_create(request):
    data = {'title': 'Create New Invoice', 'tests': Test.objects.all()}
    if request.method == 'POST':
        try:
            phone = request.POST.get('phone')
            patient = Patient.objects.get(phone=phone)
            data['success'] = create_invoice(request, patient)
        except Patient.DoesNotExist:
            patient = create_patient(request)
            data['success'] = create_invoice(request, patient)
        except Exception as e:
            data['error'] = str(e)
            
    return render(request, 'dashboard/invoice_create.html', data)


def dashboard_invoice_list(request):
    page = request.GET.get('page', 1)
    start = (page - 1) * 10
    end = page * 10
    invoices = Invoice.objects.all()
    if request.GET.get('id'):
        invoices = invoices.filter(id=request.GET.get('id'))
    invoices = invoices.order_by('-date_created')[start:end]
    data = {
        'invoices': invoices,
        'page': page,
        'title': 'Invoices',
    }
    return render(request, 'dashboard/invoice_list.html', data)


def dashboard_home_services(request):
    page = request.GET.get('page', 1)
    start = (page - 1) * 10
    end = page * 10
    invoices = Invoice.objects.filter(home_service=True)
    if request.GET.get('all') is not None:
        if request.GET.get('all') == 'true':
            invoices = invoices
        else:
            invoices = invoices.filter(home_service_date=timezone.now().date())
    else:
        invoices = invoices.filter(home_service_date=timezone.now().date())

    if request.GET.get('id') is not None:
        try:
            invoices = invoices.filter(id=request.GET.get('id'))
        except:
            pass

    invoices = invoices.order_by('-date_created')[start:end]
    data = {
        'invoices': invoices,
        'page': page,
        'title': 'Home Services',
    }
    return render(request, 'dashboard/home_services.html', data)




def dashboard_invoice_detail(request, pk):
    invoice = Invoice.objects.get(id=pk)
    invoice.save()
    data = {
        'invoice': invoice,
    }
    if request.method == 'POST':
        if request.POST.get('action') == 'add_payment':
            amount = request.POST.get('amount')
            method = request.POST.get('method')
            try:
                account = request.POST.get('account')
            except:
                account = None
            payment = Payment.objects.create(invoice=invoice, amount=amount, method=method, account=account)
            payment.save()
            invoice.save()
            messages.success(request, 'Payment added successfully')
            return redirect('dashboard_invoice_detail', pk=invoice.id)
        elif request.POST.get('action') == 'update_status':
            try:
                item = InvoiceItem.objects.get(id=int(request.POST.get('item_id')))
                item.status = request.POST.get('status')
                item.save()
            except:
                pass
        return redirect('dashboard_invoice_detail', pk=invoice.id)
    return render(request, 'dashboard/invoice_detail.html', data)


def dashboard_appointment_list(request):
    page = request.GET.get('page', 1)
    start = (page - 1) * 10
    end = page * 10
    appointments = Appointment.objects.all().order_by('-date')[start:end]
    data = {
        'appointments': appointments,
        'page': page,
        'title': 'Appointments',
    }
    return render(request, 'dashboard/appointment_list.html', data)




def get_user_email(request):
    # user_id = request.GET.get('id')
    phone = request.GET.get('phone')
    if phone:
        try:
            patient = Patient.objects.get(phone=phone)
            data = {
                'email': patient.user.email,
                'name': patient.name,
                'address': patient.address,
            }
            return JsonResponse(data)
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
