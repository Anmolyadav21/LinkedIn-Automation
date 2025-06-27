from django.contrib import admin
from .models import Signup

# Register your models here.
@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ('name','email','password')



