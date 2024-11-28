from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import json
import datetime
import qrcode
from io import BytesIO
import base64
from django.http import HttpResponse
from django.shortcuts import render
from time import time

# Create your views here.

def hello(request):
    return HttpResponse("Hello Admin...")


def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pass1']
        print(username, password)
        api_res = requests.post('http://13.233.211.102/medicalrecord/api/LaboratoryLogin/',json={'username':username,'password':password})
        print(api_res.text)
        if(api_res.json().get('message_code')==1000):
            request.session['user']= api_res.json().get('message_data')
            return redirect(index)
        
        else:
            messages.success(request, "Invalid username or password.")
            return redirect(Login)
    
    if('user' in request.session):
        return redirect(index)
    else:   
        return render(request, 'login.html')

def index(request):
    if('user' in request.session):
        api_res=requests.post('http://13.233.211.102/medicalrecord/api/get_laboratory_stats/',json={'laboratory_id':request.session.get('user').get('laboratory_id')})
        print(api_res.text)
        data= api_res.json().get('message_data')
        print(data)
        return render(request, 'index.html',{'data':data})
    else:   
        return redirect(Login)
    
def base(request):
    if('user' in request.session):
        return render(request, 'base.html', context={})
    else:   
        return redirect(Login)


def Logout(request):
    request.session.clear()
    messages.success(request, "You have successfully signed out")
    return redirect(Login)


def LaboratoryRegisteration(request):
    if(request.method == 'GET'):
        return render(request,'main/LaboratoryRegisteration.html')
    
    else:
        form_data=request.POST
        print(form_data)
        api_data = {
            "laboratory_name": form_data.get('laboratory_name'),
            "laboratory_address": form_data.get('laboratory_address'),
            "laboratory_contact_number": form_data.get('laboratory_contact_number'),
            "laboratory_owner_name": form_data.get('laboratory_owner_name'),
            "laboratory_owner_number":form_data.get('laboratory_owner_number'),
            "laboratory_username": form_data.get('username'),
            "laboratory_password": form_data.get('password'),
            "laboratory_type": 1, # 1means external
        }
        print(api_data)
        api_res = requests.post('http://13.233.211.102/medicalrecord/api/insert_laboratory/',json=api_data)
        print(api_res.text)
         
        if(api_res.json().get('message_code')==1000):
            return redirect(Login)
        else:
            return redirect(LaboratoryRegisteration)



def generate_qr_code(request):
    if('user' in request.session):
        laboratory_token = request.session.get('user').get('laboratory_token')
    else:   
        return redirect(Login)
    
    print(laboratory_token)
    url = f'https://drishtis.app/DoctorCollection/approveLaboratory/?laboratory_token={laboratory_token}'
    # url = f'http://127.0.0.1:8002/MahiEHR/approveLaboratory/?laboratory_token={laboratory_token}'
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code as a base64 string
    qr_code_bytes = BytesIO()
    qr_image.save(qr_code_bytes)
    qr_code_bytes.seek(0)
    qr_code_base64 = base64.b64encode(qr_code_bytes.read()).decode('utf-8')

    if 'download' in request.GET:
        # If the user wants to download the QR code
        response = HttpResponse(qr_code_bytes.getvalue(), content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="qrcode.png"'
        return response

    # Otherwise, display the QR code on the page
    return render(request, 'main/showQRcode.html', {'qr_code_base64': qr_code_base64, 'url': url})


def approvedDoctor(request):
    if('user' in request.session):
        api_res = requests.post('http://13.233.211.102/medicalrecord/api/get_laboratory_doctor_bylaboratoryid/',json={'laboratory_id':request.session.get('user').get('laboratory_id')})
        print(api_res.text)
        if(api_res.json().get('message_code')==1000):
            approvedata = api_res.json().get('message_data')
            print(approvedata)
        else:
            approvedata=[]
            # return HttpResponse('no approved doctor')
        
        return render(request,'main/approvedDoctor.html',{'approvedata':approvedata})
    else:   
        return redirect(Login)
    
def allpatient(request):
    if('user' in request.session):
        api_res = requests.post('http://13.233.211.102/medicalrecord/api/get_patientdetails_by_laboratory_id/',json={'laboratory_id':request.session.get('user').get('laboratory_id')})
        print(api_res.text)
        if(api_res.json().get('message_code')==1000):
            prescriptions = api_res.json().get('message_data')
            print(prescriptions)
        else:
            prescriptions=[]
            # return HttpResponse('no approved doctor')
        
        return render(request,'main/allpatient.html',{'prescriptions':prescriptions})
    else:   
        return redirect(Login)
    

def get_labs_under_patient(request ,id):
    prescription_id=id
    laboratory_id = request.session.get('user').get('laboratory_id')
    print(prescription_id,laboratory_id)
    api_res = requests.post('http://13.233.211.102/medicalrecord/api/get_labdetails_by_prescription_id/',json={'prescription_id':prescription_id})
    print(api_res.text)
    if(api_res.json().get('message_code')==1000):
        labs= api_res.json().get('message_data')
        print(labs)
    
    else:
        labs=[]
    
    return render(request,'main/labs_underpatient.html',{'labs':labs,"timestamp":int(time())})

    

def get_patient_under_doctor(request ,id):
    doctor_id=id
    laboratory_id = request.session.get('user').get('laboratory_id')
    print(doctor_id,laboratory_id)
    api_res = requests.post('http://13.233.211.102/medicalrecord/api/get_patientdetails_by_doctor_laboratory_id/',json={'doctor_id':doctor_id,'laboratory_id':laboratory_id})
    print(api_res.text)
    if(api_res.json().get('message_code')==1000):
        prescriptions= api_res.json().get('message_data')
        print(prescriptions)
    
    else:
        prescriptions=[]
    
    return render(request,'main/allpatient_underDoctor.html',{'prescriptions':prescriptions,'doctor_id':doctor_id})


def update_laboratory_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prescribelaboratory_id = data.get('prescribelaboratory_id')
            print(prescribelaboratory_id)
            laboratory_status= int(data.get('status'))
            print(laboratory_status)
            #Call the external API to reset the password
            api_response = requests.post('http://13.233.211.102/medicalrecord/api/update_laboratory_status/', json={
                'prescribelaboratory_id': prescribelaboratory_id,
                'laboratory_status': laboratory_status
            })

            print(api_response.text)
            # Parse the API response
            response_data = api_response.json()
            response_data['message_code']=1000
            if response_data['message_code'] == 1000:
                response_data['message_text'] = 'Laboratory Status Updated successfully.'
            else:
                response_data['message_text'] = response_data.get('message_text', 'Unknown error.')
        
        except Exception as e:
            response_data['message_text'] = str(e)
    
    return JsonResponse(response_data)


def update_lab_status(request):
    data=json.loads(request.body)
    print(data)
    patient_labinvestigation_id = int(data.get('lab_id'))
    patient_labtestreport_check = int(data.get('status'))
    res=requests.post('http://13.233.211.102/medicalrecord/api/update_labinvestigation_details_by_patientlabid/',json={'patient_labinvestigation_id':patient_labinvestigation_id,'patient_labtestreport_check':patient_labtestreport_check})
    print(res.text)
    return JsonResponse({'success':True})

    
def get_pdf_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            consultation_id = data.get('consultation_id')
            patient_id = data.get('patient_id')
            doctor_id = data.get('doctor_id')
            print(consultation_id,patient_id,doctor_id)
            # Assuming you have doctor_id, patient_id, and consultation_id variables
            pdf_url = f"http://13.233.211.102/medicalrecord/static/prescriptionpdfs/{doctor_id}{patient_id}{consultation_id}.pdf"
            print(pdf_url)

            response_data={}
            response_data['message_code']=1000
            response_data['pdf_url']=pdf_url
            
        except Exception as e:
            response_data['message_text'] = str(e)
    
    return JsonResponse(response_data)


def filter_patients(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            #doctor_id = int(data.get('doctorid'))
            laboratory_status = int(data.get('status'))
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            laboratory_id = request.session.get('user').get('laboratory_id')
            
            api_data={'laboratory_id':laboratory_id}
            if(laboratory_status):
                api_data['laboratory_status']=laboratory_status

            if(start_date):
                api_data['start_date']=start_date
            
            if(end_date):
                api_data['end_date']=end_date

            print(api_data)

            # Send the request to the API
            api_url = "http://13.233.211.102/medicalrecord/api/filter_patientdetails_oflaboratory_by_options/"
            response = requests.post(api_url, json=api_data)
            print(response.text)
            response_data = response.json()

            if(response_data.get('message_code')==1000):
                response_data['patients'] = response_data.get('message_data')
            else:
                response_data['patients']=[]

            
        except Exception as e:
            response_data['message_text'] = str(e)
    
    return JsonResponse(response_data)

from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt  # If you want to disable CSRF, else pass it properly in the request
def upload_pdf(request):
    if request.method == 'POST':
        lab_id = request.POST.get('lab_id')
        uploaded_file = request.FILES.get('file')
        print(lab_id,uploaded_file)
        if uploaded_file and lab_id:
           # Path to save the image (directly specifying the path)
            img_directory = 'staticfiles/assets/img'
            
            # Ensure the directory exists
            os.makedirs(img_directory, exist_ok=True)

            # Get the original file extension
            ext = os.path.splitext(uploaded_file.name)[1]
            # Rename the file with the user_id and keep the original extension
            new_file_name = f"{lab_id}{ext}"
            print(new_file_name)
            # Saving the image with its renamed name
            img_path = os.path.join(img_directory, new_file_name)
            with open(img_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            res=requests.post('http://13.233.211.102/medicalrecord/api/update_labinvestigation_details_by_patientlabid/',json={'patient_labinvestigation_id':lab_id,'patient_labtestreport':new_file_name})
            print(res.text)

            return JsonResponse({'success': True, 'message': 'PDF uploaded successfully'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid file or lab ID'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


###########################Deal#######################
def showDeals(request):
    if('user' in request.session):
        res = requests.post('http://13.233.211.102/masters/api/get_active_deals_by_visible_to/',json={"visible_to":"3","user_id":request.session.get('user').get('laboratory_id')}) #here '3' pass as a string means Laboratory
        print(res.text)
        if(res.json().get('message_code')==1000):
            alldeals = res.json().get('message_data')
        
        else:
            alldeals = []
        
        return render(request,'main/showDeals.html',{'alldeals':alldeals,"timestamp":int(time())})
    
    else:
        return redirect(Login)

@csrf_exempt
def handle_deal_action(request):
    if request.method == 'POST':
        deal_id = request.POST.get('deal_id')
        DealAction_id = request.POST.get('DealAction_id')
        action_type = request.POST.get('action_type')
         
        print(deal_id,DealAction_id,action_type)
        
        # Make request to external API
        response = requests.post(
            'http://13.233.211.102/masters/api/update_deal_action_type_by_DealactionId/',
            json={"deal_id":deal_id,"dealaction_id":DealAction_id,"dealactiontype":action_type}
        )
        print(response.text)

        # Check response status
        if response.status_code == 200 and response.json().get('message_code') == 1000:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "message": "Unable to perform action."})
    
    return JsonResponse({"success": False, "message": "Invalid request method."})






         

















































def allRegistered(request):
    url="http://13.233.211.102/doctor/api/fetch_doctors/"
    res=requests.post(url)
    # print(res.text)
    if(res.json().get('message_code')==1000):
        all_doctors=res.json().get('message_data')
        print(all_doctors)
        city_response = requests.post("http://13.233.211.102/masters/api/get_cities_by_state_id/",json={"state_id":22})
        cities = (city_response.json().get("message_data", [])).get('cities',[])
        print(cities)
        # return render(request,'main/allRegistered.html',{'all_doctors':all_doctors})
        return render(request,'main/demo.html',{'all_doctors':all_doctors,"cities": cities})

def get_doctor_details(request,id):
    print(id)

    api_url="http://13.233.211.102/doctor/api/get_doctor_by_id/"
    response=requests.post(api_url,json={'doctor_id':id})
    data=response.json().get("message_data",{})
    print(data)
    # Convert epoch timestamp to formatted date
    epoch_timestamp = data[0].get('doctor_dateofbirth', 0)
    formatted_date=datetime.datetime.fromtimestamp(epoch_timestamp).strftime( "%Y-%m-%d")
    created_on = data[0].get('createdon', 0)
    registered_date=datetime.datetime.fromtimestamp(created_on).strftime( "%d-%m-%Y")   
    print(registered_date)
    data[0]['doctor_dateofbirth'] = formatted_date
    data[0]['createdon'] = registered_date
    doctor_data=data[0]
    print(data)

    stat_res=requests.post("http://13.233.211.102/doctor/api/doctors_stats/",json={'doctor_id':id})
    print(stat_res.text)
    if(stat_res.json().get('message_code')==1000):
        stats=stat_res.json().get('message_data')
        print(stats)
        user_data = {"location_id":stats['location_id']}
        user_url = 'http://13.233.211.102/doctor/api/get_all_users_by_location/'
        user_response = requests.post(user_url,json=user_data)
        users=user_response.json().get('message_data', {})
        print(users)
        clinic_url="http://13.233.211.102/doctor/api/get_all_doctor_location/"
        response=requests.post(clinic_url,json={"doctor_location_id":stats['location_id']})
        clinic_data=(response.json().get("message_data",{}))[0]
        print(clinic_data)
    
    else:
        clinic_data=0
        users=0
        stats=0
        
    return render(request,'main/doctorDetails.html',{'doctor_data':doctor_data,'clinic_data':clinic_data,'stats':stats,'users':users})


def filter_doctors(request):
    if request.method == 'GET':
        city = request.GET.get('city')
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        print(city)
        print(start_date,'start_date')
        print(end_date,'end_date')
        data=[]
        res=requests.post("http://13.233.211.102/doctor/api/fillter_doctors/",json={"city_id": city,"start_date":start_date,"end_date":end_date})
        data=res.json().get('message_data',[])
        print(data)
        return JsonResponse({'doctors': data})

    return JsonResponse({'error': 'Invalid request'}, status=400)
    
