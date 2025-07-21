from datetime import timedelta
from django.utils import timezone
from .models import CampaignLeadStatus, SequenceStep, Campaign

def start_automation_for_campaign(campaign: Campaign):
    # Get all leads in the campaign’s lead list
    leads = campaign.lead_list.lead_set.all()

    # Get all lead IDs from the exclusion lists
    excluded_ids = set()
    for exclusion_list in campaign.exclusion_lists.all():
        excluded_ids.update(exclusion_list.lead_set.values_list('id', flat=True))

    # Filter out excluded leads
    leads_to_use = leads.exclude(id__in=excluded_ids)

    # Fetch the first sequence step (order=1)
    first_step = SequenceStep.objects.filter(campaign=campaign).order_by('order').first()
    if not first_step:
        return  # Skip if no steps defined

    for lead in leads_to_use:
        CampaignLeadStatus.objects.create(
            campaign=campaign,
            lead=lead,
            current_step=first_step,
            status='in_sequence',
            is_responded=False,
            last_action_at=None,
            next_action_at=timezone.now() + timedelta(days=first_step.wait_days)
        )
