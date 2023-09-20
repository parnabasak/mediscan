#urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import (
    PasswordResetView as auth_PasswordResetView,
    PasswordResetDoneView as auth_PasswordResetDoneView,
    PasswordResetConfirmView as auth_PasswordResetConfirmView,
    PasswordResetCompleteView as auth_PasswordResetCompleteView,
)
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('services/', services, name='services'),
    path('doctors/', doctors, name='doctors'),
    path('doctors/<int:pk>', doctor_detail, name='doctor_detail'),


    path('register/', register, name='register'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),

    path('user/', user_profile, name='user_home'),
    path('user/appointments/', user_appointments, name='user_appointments'),
    path('user/appointments/archive', user_appointments_archived, name='user_appointments_archive'),
    path('user/invoices/', user_invoices, name='user_invoice_list'),
    path('user/invoices/<int:pk>', user_invoice_detail, name='user_invoice_detail'),
    path('user/invoices/create/', user_invoice_create, name='user_invoice_create'),


    # path('reset_password/', auth_PasswordResetView.as_view(template_name='auth/password_reset.html'), name='reset_password'),
    # path('reset_password_sent/', auth_PasswordResetDoneView.as_view(template_name='auth/password_reset_sent.html'), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_PasswordResetConfirmView.as_view(template_name='auth/password_reset_form.html'), name='password_reset_confirm'),
    # path('reset_password_complete/', auth_PasswordResetCompleteView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_complete'),

    path('reset_password/', auth_PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    

    path('dashboard/', dashboard_home, name='dashboard_home'),
    path('dashboard/patients/', dashboard_patients, name='dashboard_patient_list'),
    path('dashboard/patients/<int:pk>/', dashboard_patient_detail, name='dashboard_patient_detail'),
    path('dashboard/patients/<int:pk>/edit/', dashboard_patient_edit, name='dashboard_patient_edit'),
    path('dashboard/patients/<int:pk>/delete/', dashboard_patient_delete, name='dashboard_patient_delete'),

    path('dashboard/invoices/', dashboard_invoice_list, name='dashboard_invoice_list'),
    path('dashboard/invoices/<int:pk>/', dashboard_invoice_detail, name='dashboard_invoice_detail'),
    path('dashboard/invoices/new/', dashboard_invoice_create, name='dashboard_invoice_create'),

    path('dashboard/home-services/', dashboard_home_services, name='dashboard_home_services'),

    

    path('dashboard/appointments/', dashboard_appointment_list, name='dashboard_appointment_list'),

    path('get_user_email/', get_user_email, name='get_user_email'),

]


