

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

# Proxy model - Stores proxy configurations
class Proxy(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)  # Needs secure handling
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.host}:{self.port}"

# LinkedInAccount model - Stores LinkedIn account details
class LinkedInAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Store password securely
    connected_via_extension = models.BooleanField(default=False)
    profile_name = models.CharField(max_length=255)
    profile_picture_url = models.URLField(null=True, blank=True)
    track_heyreach_conversations_only = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    daily_follows_limit = models.IntegerField(default=0)
    daily_messages_limit = models.IntegerField(default=0)
    daily_inmail_limit = models.IntegerField(default=0)
    daily_connection_request_limit = models.IntegerField(default=0)
    is_warm = models.BooleanField(default=False)
    sending_days = models.JSONField(default=list)  # e.g., ["MON", "TUE", "WED", "THU", "FRI"]
    sending_start_time = models.TimeField(null=True, blank=True)
    sending_end_time = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    proxy = models.ForeignKey(Proxy, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.profile_name} ({self.email})"

    # Override save method to hash password before saving it
    def save(self, *args, **kwargs):
        if self.password:
            self.password = make_password(self.password)  # Hash the password before saving
        super().save(*args, **kwargs)

    # Method to check if password matches the stored hashed password
    def check_password(self, password):
        return check_password(password, self.password)  # Compare the provided password with the hashed one

# LeadList model - Stores lead lists generated or imported by the user
class LeadList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    source_url = models.URLField(null=True, blank=True)  # URL used to scrape leads
    import_csv_file = models.FileField(upload_to='leads/', null=True, blank=True)  # Import leads via CSV
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Lead model - Individual lead data (scraped or imported)
class Lead(models.Model):
    lead_list = models.ForeignKey(LeadList, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    headline = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    linkedin_url = models.URLField(unique=True)
    email_address = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.linkedin_url}"

# Campaign model - Stores campaign data (e.g., outreach campaigns)
class Campaign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    lead_list = models.ForeignKey(LeadList, on_delete=models.CASCADE)
    exclusion_lists = models.ManyToManyField(LeadList, related_name='excluded_campaigns', blank=True)
    sending_accounts = models.ManyToManyField(LinkedInAccount)
    status = models.CharField(max_length=50, choices=[('draft', 'Draft'), ('active', 'Active'), ('paused', 'Paused'), ('finished', 'Finished')])
    created_at = models.DateTimeField(auto_now_add=True)
    launched_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

# SequenceStep model - Stores actions within a campaign sequence
class SequenceStep(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    order = models.IntegerField()
    action_type = models.CharField(max_length=50, choices=[
        ('CONNECTION_REQUEST', 'Connection Request'),
        ('MESSAGE', 'Message'),
        ('INMAIL', 'InMail'),
        ('VIEW_PROFILE', 'View Profile'),
        ('LIKE_POST', 'Like Post'),
    ])
    wait_days = models.IntegerField(default=0)
    message_content = models.TextField(null=True, blank=True)
    subject_line = models.CharField(max_length=255, null=True, blank=True)
    custom_variables = models.JSONField(null=True, blank=True)
    message_variations = models.JSONField(null=True, blank=True)
    fallback_message_content = models.TextField(null=True, blank=True)
    next_step_on_accepted = models.ForeignKey('self', null=True, blank=True, related_name='next_step_accepted', on_delete=models.CASCADE)
    next_step_on_not_accepted = models.ForeignKey('self', null=True, blank=True, related_name='next_step_not_accepted', on_delete=models.CASCADE)
    ends_automation_on_response = models.BooleanField(default=False)

    def __str__(self):
        return f"Step {self.order} - {self.action_type}"

# CampaignLeadStatus model - Tracks the progress of each lead within a campaign
class CampaignLeadStatus(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    current_step = models.ForeignKey(SequenceStep, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50, choices=[('in_sequence', 'In Sequence'), ('pending', 'Pending'), ('paused', 'Paused'), ('failed', 'Failed'), ('finished', 'Finished'), ('responded', 'Responded')])
    last_action_at = models.DateTimeField(null=True, blank=True)
    next_action_at = models.DateTimeField(null=True, blank=True)
    is_responded = models.BooleanField(default=False)

    def __str__(self):
        return f"Lead {self.lead} - Campaign {self.campaign}"

# Reply model - Stores replies to messages in the unified inbox
class Reply(models.Model):
    linkedin_account = models.ForeignKey(LinkedInAccount, on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message_content = models.TextField()
    sent_at = models.DateTimeField()
    received_at = models.DateTimeField()
    is_read = models.BooleanField(default=False)
    is_outbound_message = models.BooleanField()

    def __str__(self):
        return f"Reply from {self.lead} - {self.message_content[:30]}..."
