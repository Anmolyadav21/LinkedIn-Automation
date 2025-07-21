# Register your models here.
from django.contrib import admin
from .models import (
    Proxy, LinkedInAccount, LeadList, Lead, Campaign,
    SequenceStep, CampaignLeadStatus, Reply
)

admin.site.register(Proxy)
admin.site.register(LinkedInAccount)
admin.site.register(LeadList)
admin.site.register(Lead)
admin.site.register(Campaign)
admin.site.register(SequenceStep)
admin.site.register(CampaignLeadStatus)
admin.site.register(Reply)
