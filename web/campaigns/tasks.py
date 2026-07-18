import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from celery import shared_task
from runner.campaign_runner import run_campaign


@shared_task
def run_campaign_task(campaign_id, template, filters=None):
    run_campaign(campaign_id=campaign_id, template=template, filters=filters)