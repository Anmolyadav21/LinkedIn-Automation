
from django.core.management.base import BaseCommand
from tasks.models import Campaign, CampaignLeadStatus, SequenceStep
from django.utils import timezone
from tasks.utils.campaign_automation import start_automation_for_campaign  # Import the function from utils

class Command(BaseCommand):
    help = 'Processes campaigns and sends messages based on sequence steps'

    def handle(self, *args, **kwargs):
        # Get all active campaigns
        now = timezone.now()
        campaigns = Campaign.objects.filter(status='active')

        for campaign in campaigns:
            self.stdout.write(self.style.SUCCESS(f"Processing campaign: {campaign.name}"))

            # Get all leads in sequence that are due for an action
            leads = CampaignLeadStatus.objects.filter(
                campaign=campaign,
                status='pending',
                next_action_at__lte=now
            ).select_related('lead', 'current_step')

            for lead_status in leads:
                step = lead_status.current_step
                lead = lead_status.lead

                self.stdout.write(f"- Lead: {lead.first_name} {lead.last_name} @ {lead.linkedin_url}")
                # Trigger sending of the LinkedIn message
                start_automation_for_campaign(campaign)

                # Determine the next step and update lead status
                next_step = step.next_step_on_accepted
                if next_step:
                    lead_status.current_step = next_step
                    lead_status.next_action_at = now + timezone.timedelta(days=next_step.wait_days)
                else:
                    lead_status.status = 'finished'
                lead_status.save()

            self.stdout.write(self.style.SUCCESS(f"Campaign {campaign.name} processed successfully"))
