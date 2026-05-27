from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages as django_messages
from .models import Campaign, CampaignLog, Contact
import sys
import os
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from runner.campaign_runner import run_campaign


def dashboard(request):
    campaigns = Campaign.objects.all()
    logs = {log.campaign_id: log for log in CampaignLog.objects.order_by('-completed_at')}
    for campaign in campaigns:
        campaign.log = logs.get(campaign.id)
    has_running_campaigns = campaigns.filter(status='running').exists()
    return render(request, 'campaigns/dashboard.html', {
        'campaigns': campaigns,
        'has_running_campaigns': has_running_campaigns,
    })


def new_campaign(request):
    cities = Contact.objects.values_list('city', flat=True).distinct().exclude(city=None)
    categories = Contact.objects.values_list('category', flat=True).distinct().exclude(category=None)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        template = request.POST.get('template', '').strip()
        city = request.POST.get('city', '').strip()
        category = request.POST.get('category', '').strip()

        if not name or not template:
            django_messages.error(request, 'Campaign name and message template are required.')
            return render(request, 'campaigns/new_campaign.html', {
                'cities': cities,
                'categories': categories,
            })

        filters = {}
        if city:
            filters['city'] = city
        if category:
            filters['category'] = category

        try:
            campaign = Campaign.objects.create(
                name=name,
                template=template,
                segment_filter=filters if filters else {}
            )

            thread = threading.Thread(
                target=run_campaign,
                kwargs={
                    'campaign_id': str(campaign.id),
                    'template': template,
                    'filters': filters if filters else None,
                },
                daemon=True
            )
            thread.start()

            django_messages.success(request, f'Campaign "{name}" launched. Check dashboard for status.')
            return redirect('dashboard')

        except Exception as e:
            django_messages.error(request, f'Failed to launch campaign: {str(e)}')
            return render(request, 'campaigns/new_campaign.html', {
                'cities': cities,
                'categories': categories,
            })

    return render(request, 'campaigns/new_campaign.html', {
        'cities': cities,
        'categories': categories,
    })


def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    log = CampaignLog.objects.filter(campaign=campaign).order_by('-completed_at').first()
    return render(request, 'campaigns/campaign_detail.html', {
        'campaign': campaign,
        'log': log,
    })