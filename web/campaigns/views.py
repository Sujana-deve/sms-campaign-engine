from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Campaign, Contact
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def dashboard(request):
    campaigns = Campaign.objects.all()
    return render(request, 'campaigns/dashboard.html', {'campaigns': campaigns})

def new_campaign(request):
    cities = Contact.objects.values_list('city', flat=True).distinct().exclude(city=None)
    business_types = Contact.objects.values_list('business_type', flat=True).distinct().exclude(business_type=None)

    if request.method == 'POST':
        name = request.POST.get('name')
        template = request.POST.get('template')
        city = request.POST.get('city', '')
        business_type = request.POST.get('business_type', '')

        filters = {}
        if city:
            filters['city'] = city
        if business_type:
            filters['business_type'] = business_type

        from runner.campaign_runner import CampaignRunner
        runner = CampaignRunner()
        runner.run(campaign_name=name, message_template=template, filters=filters)

        messages.success(request, f'Campaign "{name}" launched successfully.')
        return redirect('dashboard')

    return render(request, 'campaigns/new_campaign.html', {
        'cities': cities,
        'business_types': business_types,
    })

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'campaigns/campaign_detail.html', {'campaign': campaign})