from django.utils import timezone
from datetime import timedelta
from tasks.models import CampaignLeadStatus, Campaign, Lead, SequenceStep

def start_automation_for_campaign(campaign: Campaign):
    # Get all leads from the lead list associated with the campaign
    leads = campaign.lead_list.lead_set.all()

    # Exclude leads from exclusion lists
    excluded_ids = set()
    for exclusion in campaign.exclusion_lists.all():
        excluded_ids.update(exclusion.lead_set.values_list('id', flat=True))

    # Filter leads to exclude those in the exclusion lists
    leads_to_use = leads.exclude(id__in=excluded_ids)

    # Get the first sequence step
    first_step = SequenceStep.objects.filter(campaign=campaign).order_by('order').first()

    if not first_step:
        return  # No steps found, so exit the function

    # Iterate through the leads to create campaign lead status
    for lead in leads_to_use:
        # Create or update CampaignLeadStatus for each lead
        CampaignLeadStatus.objects.create(
            campaign=campaign,
            lead=lead,
            current_step=first_step,
            status='pending',
            is_responded=False,
            last_action_at=None,
            next_action_at=timezone.now() + timedelta(days=first_step.wait_days)
        )
