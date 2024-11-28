from django.contrib import admin
from django.urls import path
from .views import *


urlpatterns = [
    path('hello/',hello,name='hello'),
    path('login/',Login,name='login'),
    path('base/',base,name='base'),
    path('index/',index,name='index'),
    path('Logout/',Logout,name='Logout'),
    path('allRegistered/',allRegistered,name='allRegistered'),
    path('get_doctor_details/<int:id>',get_doctor_details,name='get_doctor_details'),
    path('filter_doctors/',filter_doctors, name='filter_doctors'),
    path('LaboratoryRegisteration/',LaboratoryRegisteration,name='LaboratoryRegisteration'),
    path('generate_qr_code/',generate_qr_code,name='generate_qr_code'),
    path('approvedDoctor/',approvedDoctor,name='approvedDoctor'),
    path('get_patient_under_doctor/<int:id>',get_patient_under_doctor,name='get_patient_under_doctor'),
    path('update_laboratory_status/',update_laboratory_status,name='update_laboratory_status'),
    path('get_pdf_url/',get_pdf_url,name='get_pdf_url'),
    path('filter_patients/',filter_patients,name='filter_patients'),
    path('upload_pdf/',upload_pdf,name='upload_pdf'),
    path('allpatient/',allpatient,name='allpatient'),
    path('get_labs_under_patient/<int:id>',get_labs_under_patient,name='get_labs_under_patient'),
    path('update_lab_status/',update_lab_status,name='update_lab_status'),

    #####################Deal#############################
    path('showDeals/',showDeals,name='showDeals'),
    path('handle_deal_action/',handle_deal_action, name='handle_deal_action'),
    
]
