from django.shortcuts import render,redirect,reverse
from django.contrib.auth import logout
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms

def home_view(request):
    x=models.Stock.objects.all()
    print(x)
    if len(x)==0:
        blood1=models.Stock()
        blood1.bloodgroup="A+"
        blood1.save()

        blood2=models.Stock()
        blood2.bloodgroup="A-"
        blood2.save()

        blood3=models.Stock()
        blood3.bloodgroup="B+"
        blood3.save()        

        blood4=models.Stock()
        blood4.bloodgroup="B-"
        blood4.save()

        blood5=models.Stock()
        blood5.bloodgroup="AB+"
        blood5.save()

        blood6=models.Stock()
        blood6.bloodgroup="AB-"
        blood6.save()

        blood7=models.Stock()
        blood7.bloodgroup="O+"
        blood7.save()

        blood8=models.Stock()
        blood8.bloodgroup="O-"
        blood8.save()

    if request.user.is_authenticated:
        return redirect('afterlogin')  
    return render(request,'blood/index.html')

def is_donor(user):
    return user.groups.filter(name='DONOR').exists() or dmodels.Donor.objects.filter(user=user).exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists() or pmodels.Patient.objects.filter(user=user).exists()


def afterlogin_view(request):
    if is_donor(request.user):      
        return redirect('donor-dashboard')
                
    elif is_patient(request.user):
        return redirect('patient-dashboard')
    else:
        return redirect('admin-dashboard')

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def admin_dashboard_view(request):
    totalunit=models.Stock.objects.aggregate(Sum('unit'))
    
    # Calculate unique donor names from approved donations
    approved_donations = dmodels.BloodDonate.objects.filter(status='Approved')
    unique_donors = set()
    for d in approved_donations:
        name = d.donor_name or (d.donor.get_name if d.donor else "")
        if name:
            unique_donors.add(name.strip().lower())
            
    dict={

        'A1':models.Stock.objects.get(bloodgroup="A+"),
        'A2':models.Stock.objects.get(bloodgroup="A-"),
        'B1':models.Stock.objects.get(bloodgroup="B+"),
        'B2':models.Stock.objects.get(bloodgroup="B-"),
        'AB1':models.Stock.objects.get(bloodgroup="AB+"),
        'AB2':models.Stock.objects.get(bloodgroup="AB-"),
        'O1':models.Stock.objects.get(bloodgroup="O+"),
        'O2':models.Stock.objects.get(bloodgroup="O-"),
        'totaldonors':len(unique_donors),
        'totalbloodunit':totalunit['unit__sum'],
        'totalrequest':models.BloodRequest.objects.all().count(),
        'totalapprovedrequest':models.BloodRequest.objects.all().filter(status='Approved').count()
    }
    return render(request,'blood/admin_dashboard.html',context=dict)

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def admin_blood_view(request):
    dict={
        'bloodForm':forms.BloodForm(),
        'A1':models.Stock.objects.get(bloodgroup="A+"),
        'A2':models.Stock.objects.get(bloodgroup="A-"),
        'B1':models.Stock.objects.get(bloodgroup="B+"),
        'B2':models.Stock.objects.get(bloodgroup="B-"),
        'AB1':models.Stock.objects.get(bloodgroup="AB+"),
        'AB2':models.Stock.objects.get(bloodgroup="AB-"),
        'O1':models.Stock.objects.get(bloodgroup="O+"),
        'O2':models.Stock.objects.get(bloodgroup="O-"),
    }
    if request.method=='POST':
        bloodForm=forms.BloodForm(request.POST)
        if bloodForm.is_valid() :        
            bloodgroup=bloodForm.cleaned_data['bloodgroup']
            stock=models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit=bloodForm.cleaned_data['unit']
            stock.save()
        return redirect('admin-blood')
    return render(request,'blood/admin_blood.html',context=dict)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def admin_donor_view(request):
    donors=dmodels.Donor.objects.all()
    return render(request,'blood/admin_donor.html',{'donors':donors})

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=dmodels.User.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    userForm.fields['password'].required = False
    donorForm=dforms.DonorForm(instance=donor)
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        userForm.fields['password'].required = False
        donorForm=dforms.DonorForm(request.POST,request.FILES,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save(commit=False)
            new_password = userForm.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return redirect('admin-donor')

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def admin_patient_view(request):
    patients=pmodels.Patient.objects.all()
    return render(request,'blood/admin_patient.html',{'patients':patients})


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def update_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=pmodels.User.objects.get(id=patient.user_id)
    userForm=pforms.PatientUserForm(instance=user)
    userForm.fields['password'].required = False
    patientForm=pforms.PatientForm(instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        userForm.fields['password'].required = False
        patientForm=pforms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save(commit=False)
            new_password = userForm.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-patient')

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def admin_request_view(request):
    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests})

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def admin_request_history_view(request):
    requests=models.BloodRequest.objects.all()
    return render(request,'blood/admin_request_history.html',{'requests':requests})

@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser, login_url='admin-login')
def admin_donation_view(request):
    donations=dmodels.BloodDonate.objects.all()
    return render(request,'blood/admin_donation.html',{'donations':donations})

@login_required(login_url='admin-login')
def update_approve_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    message=None
    bloodgroup=req.bloodgroup
    unit=req.unit
    stock=models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit > unit:
        stock.unit=stock.unit-unit
        stock.save()
        req.status="Approved"
        
    else:
        message="Stock Doest Not Have Enough Blood To Approve This Request, Only "+str(stock.unit)+" Unit Available"
    req.save()

    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests,'message':message})

@login_required(login_url='admin-login')
def update_reject_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    req.status="Rejected"
    req.save()
    return redirect('admin-request')

@login_required(login_url='admin-login')
def approve_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group=donation.bloodgroup
    donation_blood_unit=donation.unit

    stock=models.Stock.objects.get(bloodgroup=donation_blood_group)
    stock.unit=stock.unit+donation_blood_unit
    stock.save()

    donation.status='Approved'
    donation.save()
    return redirect('admin-donation')


@login_required(login_url='admin-login')
def reject_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation.delete()
    return redirect('admin-donation')

def logout_view(request):
    logout(request)
    return render(request, 'blood/logout.html')
