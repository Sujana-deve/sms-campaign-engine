from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Campaign, CampaignLog, Contact
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from runner.campaign_runner import run_campaign


def dashboard(request):
    campaigns = Campaign.objects.all()
    logs = {log.campaign_id: log for log in CampaignLog.objects.order_by('-completed_at')}
    for campaign in campaigns:
        campaign.log = logs.get(campaign.id)
    return render(request, 'campaigns/dashboard.html', {'campaigns': campaigns})


def new_campaign(request):
    cities = Contact.objects.values_list('city', flat=True).distinct().exclude(city=None)
    categories = Contact.objects.values_list('category', flat=True).distinct().exclude(category=None)

    if request.method == 'POST':
        name = request.POST.get('name')
        template = request.POST.get('template')
        city = request.POST.get('city', '')
        category = request.POST.get('category', '')

        filters = {}
        if city:
            filters['city'] = city
        if category:
            filters['category'] = category

        campaign = Campaign.objects.create(
            name=name,
            template=template,
        )

        run_campaign(
            campaign_id=str(campaign.id),
            template=template,
            filters=filters if filters else None
        )

        messages.success(request, f'Campaign "{name}" launched successfully.')
        return redirect('dashboard')

    return render(request, 'campaigns/new_campaign.html', {
        'cities': cities,
        'categories': categories,
    })


def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    try:
        log = CampaignLog.objects.filter(campaign=campaign).order_by('-completed_at').first()
    except CampaignLog.DoesNotExist:
        log = None
    return render(request, 'campaigns/campaign_detail.html', {
        'campaign': campaign,
        'log': log,
    })