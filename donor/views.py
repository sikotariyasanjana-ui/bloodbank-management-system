from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
            return redirect('donor-login')
    return render(request,'donor/signup.html',context=mydict)


@login_required(login_url='donor-login')
@user_passes_test(lambda u: u.groups.filter(name='DONOR').exists() or models.Donor.objects.filter(user=u).exists(), login_url='donor-login')
def donor_dashboard_view(request):
    try:
        donor = models.Donor.objects.get(user_id=request.user.id)
    except models.Donor.DoesNotExist:
        return redirect('donor-signup')
    dict={
        'donationpending': models.BloodDonate.objects.all().filter(donor=donor).filter(status='Pending').count(),
        'donationapproved': models.BloodDonate.objects.all().filter(donor=donor).filter(status='Approved').count(),
        'donationmade': models.BloodDonate.objects.all().filter(donor=donor).count(),
        'donationrejected': models.BloodDonate.objects.all().filter(donor=donor).filter(status='Rejected').count(),
    }
    return render(request,'donor/dashboard.html',context=dict)


def donate_blood_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    donation_form=forms.DonationForm()
    if request.method=='POST':
        donation_form=forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate=donation_form.save(commit=False)
            blood_donate.bloodgroup=donation_form.cleaned_data['bloodgroup']
            blood_donate.donor=donor
            
            # Save the donor name directly to the donation record
            donor_name = request.POST.get('donor_name')
            if donor_name:
                blood_donate.donor_name = donor_name
                
            blood_donate.save()
            return redirect('donation-history')  
    return render(request,'donor/donate_blood.html',{'donation_form':donation_form, 'donor':donor})

def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.BloodDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})

def make_request_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            blood_request.request_by_donor=donor
            blood_request.save()
            return redirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form, 'donor':donor})

def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    blood_requests=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_requests':blood_requests})
from django.http import HttpResponse

def home(request):
    return HttpResponse("Blood Bank Project Running 🩸")
