
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'tasks'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # LinkedIn Account
    # path('login/', views.linkedin_login_view, name='login'),  # Login view
    path('logout/', views.logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('linkedin/create/', views.create_linkedin_account, name='create_linkedin_account'),
    path('linkedin/<int:account_id>/edit/', views.update_linkedin_account, name='update_linkedin_account'),
    path('linkedin/<int:account_id>/delete/', views.delete_linkedin_account, name='delete_linkedin_account'),
    path('create-linkedin-account/', views.create_linkedin_account, name='create_linkedin_account'),

    # Lead List
    path('lead-list/create/', views.create_lead_list, name='create_lead_list'),
    path('lead-list/<int:lead_list_id>/', views.view_lead_list, name='view_lead_list'),

    # Campaigns
    path('campaigns/', views.list_campaigns, name='list_campaigns'),
    # path('campaign/create/', views.create_campaign, name='create_campaign'),
    path('create-campaign/', views.create_campaign, name='create_campaign'),
    path('campaign/<int:campaign_id>/', views.view_campaign, name='view_campaign'),
    path('campaign/<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),
    path('campaign/<int:campaign_id>/launch/', views.launch_campaign, name='launch_campaign'),

    # Sequence Steps
    path('campaign/<int:campaign_id>/sequence/create/', views.create_sequence_step, name='create_sequence_step'),

    # Inbox / Replies
    path('replies/', views.view_replies, name='view_replies'),
    path('replies/<int:reply_id>/read/', views.mark_reply_as_read, name='mark_reply_as_read'),


    # path('linkedin-login/', views.linkedin_login_view, name='linkedin-login'),
    # path('login/', views.linkedin_login_view, name='login'),  # Login view
    # path('logout/', views.logout_view, name='logout'),  # Logout view
    # path('create-linkedin-account/', views.create_linkedin_account, name='create_linkedin_account'),
    # Create LinkedIn account

]
