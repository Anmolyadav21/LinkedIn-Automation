from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
import csv
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from io import TextIOWrapper
from .forms import LinkedInLoginForm
from django.contrib.auth import logout
from django.contrib.auth.models import AnonymousUser
from .forms import LinkedInAccountForm
from .models import (
    LinkedInAccount, LeadList, Lead,
    Campaign, SequenceStep, CampaignLeadStatus, Reply
)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import LinkedInAccountForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .forms import LeadListForm
from .models import LeadList
from django.utils import timezone
from .models import Campaign
from .utils.campaign_automation import start_automation_for_campaign
from .models import Campaign, SequenceStep
from django.contrib.auth.models import AnonymousUser
import time



@login_required
def dashboard(request):
    if isinstance(request.user, AnonymousUser):
        return redirect('login')  # Redirect to login if the user is not authenticated

    linkedin_accounts = LinkedInAccount.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'linkedin_accounts': linkedin_accounts})

# LinkedIn login using Selenium
def linkedin_login(driver, email, password):
    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        email_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        email_field.send_keys(email)
        password_field.send_keys(password)

        sign_in_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        sign_in_button.click()

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/feed/')]"))
        )
        print("Login successful.")
        return True
    except TimeoutException:
        print("Login failed: Timeout. Could not load the page or sign in.")
        return False
    except Exception as e:
        print(f"Login failed: {e}")
        return False

# LinkedIn Login View
def linkedin_login_view(request):
    if request.method == 'POST':
        form = LinkedInLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Set up Selenium WebDriver
            options = Options()
            options.add_argument("--headless")  # Run in the background
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

            # Call linkedin_login with the credentials
            if linkedin_login(driver, email, password):
                messages.success(request, "Successfully logged in to LinkedIn!")
                driver.quit()
                return redirect('tasks:create_campaign')  # Redirect to create campaign page
            else:
                messages.error(request, "Failed to log in. Please check your credentials.")
                driver.quit()
                return redirect('login')  # Redirect to login page on failure
    else:
        form = LinkedInLoginForm()

    return render(request, 'linkedin_login.html', {'form': form})

# LinkedIn Account Creation View
@login_required
def create_linkedin_account(request):
    if request.method == 'POST':
        form = LinkedInAccountForm(request.POST)
        if form.is_valid():
            linkedin_account = form.save(commit=False)
            linkedin_account.user = request.user  # Add the logged-in user to the LinkedIn account
            linkedin_account.save()  # Save the account to the database
            messages.success(request, "LinkedIn account created successfully!")

            if request.user.is_superuser:
                print("Redirecting admin to create campaign page")  # Debugging line
                # Redirect to the create campaign page if the user is an admin
                return redirect('tasks:create_campaign')

            return redirect('tasks:create_campaign')  # Redirect to create campaign after account creation
    else:
        form = LinkedInAccountForm()

    return render(request, 'create_linkedin_account.html', {'form': form})

@login_required
def delete_linkedin_account(request, account_id):
    # Get the LinkedIn account for the logged-in user
    account = get_object_or_404(LinkedInAccount, id=account_id, user=request.user)

    # Delete the account
    account.delete()
    messages.success(request, "LinkedIn account deleted successfully!")

    return redirect('tasks:dashboard')  # Redirect to the dashboard or any other page

@login_required
def create_lead_list(request):
    if request.method == 'POST':
        form = LeadListForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the new lead list
            lead_list = form.save(commit=False)
            lead_list.user = request.user  # Associate the lead list with the logged-in user
            lead_list.save()

            messages.success(request, "Lead List created successfully!")
            return redirect('tasks:view_lead_list', lead_list.id)  # Redirect to the created lead list view
    else:
        form = LeadListForm()

    return render(request, 'create_lead_list.html', {'form': form})

@login_required
def view_lead_list(request, lead_list_id):
    # Get the LeadList object for the logged-in user
    lead_list = get_object_or_404(LeadList, id=lead_list_id, user=request.user)

    # You can add any filtering or searching functionality here if needed
    search = request.GET.get('search', '')
    leads = Lead.objects.filter(lead_list=lead_list, first_name__icontains=search)

    return render(request, 'view_lead_list.html', {'lead_list': lead_list, 'leads': leads})

@login_required
def list_campaigns(request):
    # Retrieve all campaigns for the logged-in user
    campaigns = Campaign.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'list_campaigns.html', {'campaigns': campaigns})

@login_required
def create_campaign(request):
    if request.method == 'POST':
        name = request.POST['name']
        lead_list_id = request.POST['lead_list']
        account_ids = request.POST.getlist('sending_accounts')
        exclusion_ids = request.POST.getlist('exclusion_lists')

        lead_list = get_object_or_404(LeadList, id=lead_list_id, user=request.user)

        campaign = Campaign.objects.create(
            user=request.user,
            name=name,
            lead_list=lead_list,
            status='draft'
        )

        campaign.sending_accounts.set(
            LinkedInAccount.objects.filter(id__in=account_ids, user=request.user)
        )
        campaign.exclusion_lists.set(
            LeadList.objects.filter(id__in=exclusion_ids, user=request.user)
        )

        messages.success(request, f"{name} campaign created successfully.")
        return redirect('tasks:view_campaign', campaign.id)  # Redirect to view campaign page

    lead_lists = LeadList.objects.filter(user=request.user)
    accounts = LinkedInAccount.objects.filter(user=request.user)

    return render(request, 'create_campaign.html', {
        'lead_lists': lead_lists,
        'accounts': accounts,
    })


@login_required
def view_campaign(request, campaign_id):
    # Get the campaign by its ID
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)

    # Additional logic for rendering the campaign's information (if necessary)
    return render(request, 'view_campaign.html', {
        'campaign': campaign
    })

@login_required
def delete_campaign(request, campaign_id):
    # Get the campaign by its ID
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)

    # Delete the campaign
    campaign.delete()

    # Show a success message to the user
    messages.success(request, "Campaign deleted successfully!")

    # Redirect to the list of campaigns after deletion
    return redirect('tasks:list_campaigns')

@login_required
def launch_campaign(request, campaign_id):
    # Get the campaign object by ID
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)

    # Check if the campaign is not already launched
    if campaign.status != 'draft':
        messages.warning(request, "Campaign is already launched or cannot be launched.")
        return redirect('tasks:view_campaign', campaign.id)  # Or any page you want to redirect to

    # Change the campaign status to active and record the launch time
    campaign.status = 'active'
    campaign.launched_at = timezone.now()
    campaign.save()

    # Call the function to start the campaign automation (you need to define this function)
    start_automation_for_campaign(campaign)

    # Show success message and redirect to the campaign view page
    messages.success(request, "Campaign successfully launched and automation started.")
    return redirect('tasks:view_campaign', campaign.id)


@login_required
def create_sequence_step(request, campaign_id):
    # Get the campaign by its ID
    campaign = get_object_or_404(Campaign, id=campaign_id, user=request.user)

    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        message_content = request.POST.get('message_content', '')
        wait_days = request.POST.get('wait_days', 1)

        # Create the new sequence step for the campaign
        new_step = SequenceStep.objects.create(
            campaign=campaign,
            action_type=action_type,
            message_content=message_content,
            wait_days=wait_days,
            order=SequenceStep.objects.filter(campaign=campaign).count() + 1  # Ensuring correct order
        )

        messages.success(request, f"Sequence step {new_step.order} added successfully!")
        return redirect('tasks:view_campaign', campaign.id)  # Redirect to the campaign view page

    return HttpResponse("Invalid request", status=400)


@login_required
def view_replies(request):
    # Fetch all replies for the logged-in user
    replies = Reply.objects.filter(linkedin_account__user=request.user).order_by('-received_at')

    # Paginate replies, 10 per page
    paginator = Paginator(replies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_replies.html', {'replies': page_obj})

@login_required
def mark_reply_as_read(request, reply_id):
    # Get the reply object by ID
    reply = get_object_or_404(Reply, id=reply_id, linkedin_account__user=request.user)

    # Mark the reply as read
    reply.is_read = True
    reply.save()

    # Display success message
    messages.success(request, f"Reply from {reply.linkedin_account.profile_name} marked as read.")

    # Redirect to view replies page or wherever you'd like
    return redirect('tasks:view_replies')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # or wherever you want to redirect after login
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')  # stay on the login page if authentication fails
    return render(request, 'login.html')

# Logout view
@login_required
def logout_view(request):
    logout(request)  # Logs out the user
    return redirect('login')  # Redirects to the login page after logging out


@login_required
def update_linkedin_account(request, account_id):
    # Get the LinkedIn account by id
    account = get_object_or_404(LinkedInAccount, id=account_id, user=request.user)

    if request.method == 'POST':
        account.email = request.POST['email']
        account.profile_name = request.POST['profile_name']
        account.save()

        messages.success(request, f"{account.profile_name} updated.")
        return redirect('tasks:dashboard')  # Redirect back to dashboard or any other view after updating

    return render(request, 'update_linkedin_account.html', {'account': account})